import ast
from pathlib import Path

import pytest

from poop import Interpreter
from poop.errors import (
    ExecutionError,
    ParseError,
    TransformError,
    ValidationError,
)
from poop.transformers.boolean import BooleanTransformer
from poop.types.boolean import Boolean
from poop.types.float import Float
from poop.types.int import Int
from poop.types.tuple import Tuple


def test_valid_code_runs_successfully() -> None:
    Interpreter().run_source("x = 1 + 2")


def test_syntax_error_raises_parse_error() -> None:
    with pytest.raises(ParseError):
        Interpreter().run_source("def :")


def test_if_statement_raises_validation_error() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Interpreter().run_source("if True:\n    pass")
    assert "if statements" in str(exc_info.value)


def test_if_expression_raises_validation_error() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Interpreter().run_source("x = 1 if True else 2")
    assert "ternary" in str(exc_info.value)


def test_error_message_includes_line_number() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Interpreter().run_source("x = 1\nif True:\n    pass")
    assert "line 2" in str(exc_info.value)


def test_runtime_error_raises_execution_error() -> None:
    with pytest.raises(ExecutionError):
        Interpreter().run_source("x = 1 / 0")


def test_custom_validators_replace_defaults() -> None:
    Interpreter(validators=[]).run_source("if True:\n    pass")


def test_transformer_failure_raises_transform_error() -> None:
    class BoomTransformer:
        def transform(self, tree: ast.Module) -> ast.Module:
            raise RuntimeError("boom")

    with pytest.raises(TransformError) as exc_info:
        Interpreter(transformers=[BoomTransformer()]).run_source("x = 1")
    assert "boom" in str(exc_info.value)
    assert "BoomTransformer" in str(exc_info.value)
    assert exc_info.value.transformer == "BoomTransformer"
    assert isinstance(exc_info.value.__cause__, RuntimeError)


def test_run_file_reads_and_executes(tmp_path: Path) -> None:
    f = tmp_path / "hello.py"
    f.write_text("x = 42\n", encoding="utf-8")
    Interpreter().run_file(f)


def test_true_literal_becomes_boolean_instance() -> None:
    assert isinstance(BooleanTransformer.BINDINGS["_poop_true"], Boolean)


def test_false_literal_becomes_boolean_instance() -> None:
    assert isinstance(BooleanTransformer.BINDINGS["_poop_false"], Boolean)


def test_custom_transformers_bypass_boolean_substitution() -> None:
    tree = ast.parse("x = True")
    compiled = compile(tree, "<string>", mode="exec")
    ns: dict[str, object] = {}
    exec(compiled, ns)  # noqa: S102
    assert ns["x"] is True
    assert not isinstance(ns["x"], Boolean)


def test_int_divmod_returns_tuple_of_ints() -> None:
    result = Int(17).divmod(Int(5))
    assert isinstance(result, Tuple)
    assert result.at(Int(0)) == Int(3)
    assert result.at(Int(1)) == Int(2)


def test_float_divmod_returns_tuple_of_floats() -> None:
    result = Float(17.0).divmod(Float(5.0))
    assert isinstance(result, Tuple)
    quotient, remainder = result._items
    assert isinstance(quotient, Float)
    assert isinstance(remainder, Float)
    assert quotient._value == pytest.approx(3.0)
    assert remainder._value == pytest.approx(2.0)


def test_subscript_raises_validation_error() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Interpreter().run_source("x = [1, 2, 3]\ny = x[0]")
    assert "obj.at(key)" in str(exc_info.value)


def test_slice_subscript_is_forbidden() -> None:
    # no_subscript now also blocks slice notation
    with pytest.raises(ValidationError):
        Interpreter().run_source("x = [1, 2, 3]\ny = x[1:2]")


def test_async_method_inside_class_raises() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Interpreter().run_source(
            "class Foo:\n    async def bar(self):\n        return 1\nFoo()\n"
        )
    assert "async def is forbidden" in str(exc_info.value)


def test_free_async_function_raises() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Interpreter().run_source("async def foo():\n    return 1\n")
    assert "async def is forbidden" in str(exc_info.value)


def test_async_for_reports_the_async_def_root_cause() -> None:
    # no_async runs ahead of no_loops on purpose: fixing the `async for`
    # would only surface the async def ban on the next run.
    with pytest.raises(ValidationError) as exc_info:
        Interpreter().run_source(
            "class Foo:\n"
            "    async def bar(self):\n"
            "        async for x in self.items():\n"
            "            x\n"
        )
    assert "async def is forbidden" in str(exc_info.value)


def test_async_with_reports_the_async_def_root_cause() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Interpreter().run_source(
            "class Foo:\n"
            "    async def bar(self):\n"
            "        async with self.lock() as l:\n"
            "            l\n"
        )
    assert "async def is forbidden" in str(exc_info.value)


def test_async_generator_raises() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Interpreter().run_source(
            "class Foo:\n    async def bar(self):\n        yield 1\n"
        )
    assert "async def is forbidden" in str(exc_info.value)


def test_validators_only_still_reports_the_specific_async_construct() -> None:
    # The async rows in no_loops / no_with / no_free_functions stay useful:
    # validate_all collects every error, not just the first.
    errors = Interpreter().validate_all(
        "class Foo:\n"
        "    async def bar(self):\n"
        "        async for x in self.items():\n"
        "            x\n"
    )
    messages = [str(e) for e in errors]
    assert any("async def is forbidden" in m for m in messages)
    assert any("async for" in m for m in messages)


def test_validate_all_reports_every_occurrence_not_just_the_first() -> None:
    # Three `if`s used to answer exactly one, making a migration a
    # fix-one/rerun/repeat loop.
    errors = Interpreter().validate_all(
        "class C:\n"
        "    def m(self):\n"
        "        if a:\n"
        "            pass\n"
        "        if b:\n"
        "            pass\n"
        "        if c:\n"
        "            pass\n"
    )
    assert [e.lineno for e in errors] == [3, 5, 7]


def test_validate_all_reports_in_source_order() -> None:
    # Emitted in DEFAULT_VALIDATORS order before: lines 3, 4, 5, 6 came back
    # as 5, 6, 4, 3.
    errors = Interpreter().validate_all(
        "class C:\n"
        "    def m(self):\n"
        "        x = len(a)\n"
        "        y = a and b\n"
        "        z = print(c)\n"
        "        w = not d\n"
    )
    assert [e.lineno for e in errors] == [3, 4, 5, 6]


def test_validate_all_sorts_by_column_within_a_line() -> None:
    errors = Interpreter().validate_all(
        "class C:\n    def m(self):\n        len(print(a))\n"
    )
    assert [e.col_offset for e in errors] == sorted(e.col_offset for e in errors)
    assert len(errors) == 2


def test_validate_all_descends_into_a_rejected_node() -> None:
    # An `if` inside an `if` is two rewrites; reporting only the outer one
    # would restore the fix-one/rerun loop.
    errors = Interpreter().validate_all(
        "class C:\n"
        "    def m(self):\n"
        "        if a:\n"
        "            if b:\n"
        "                pass\n"
    )
    assert [e.lineno for e in errors] == [3, 4]


def test_validate_all_reports_a_chained_comparison_once() -> None:
    # `in` twice in one Compare is one node and one rewrite.
    errors = Interpreter().validate_all(
        "class C:\n    def m(self):\n        a in b in c\n"
    )
    assert len(errors) == 1


def test_run_source_still_stops_at_the_first_error() -> None:
    # Collecting is for --validators-only; running a program still fails fast.
    with pytest.raises(ValidationError):
        Interpreter().run_source(
            "class C:\n    def m(self):\n        if a:\n            pass\n"
        )
