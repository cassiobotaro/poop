import ast
from pathlib import Path

import pytest

from poop import Interpreter
from poop.errors import ExecutionError, ParseError, ValidationError
from poop.transformers.boolean import BooleanTransformer
from poop.types.boolean import Boolean


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
    from poop.types.int import Int
    from poop.types.tuple import Tuple

    result = Int(17).divmod(Int(5))
    assert isinstance(result, Tuple)
    assert result.at(Int(0)) == Int(3)
    assert result.at(Int(1)) == Int(2)


def test_float_divmod_returns_tuple_of_floats() -> None:
    from poop.types.float import Float
    from poop.types.int import Int
    from poop.types.tuple import Tuple

    result = Float(17.0).divmod(Float(5.0))
    assert isinstance(result, Tuple)
    assert result.at(Int(0)) == Float(3.0)
    assert result.at(Int(1)) == Float(2.0)


def test_subscript_raises_validation_error() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Interpreter().run_source("x = [1, 2, 3]\ny = x[0]")
    assert "obj.at(key)" in str(exc_info.value)


def test_slice_subscript_is_allowed() -> None:
    # no_subscript permite fatiamento — pode falhar em execução, mas não em validação
    with pytest.raises(ExecutionError):
        Interpreter().run_source("x = [1, 2, 3]\ny = x[1:2]")
