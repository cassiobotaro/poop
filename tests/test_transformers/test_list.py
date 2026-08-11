import ast

import pytest

from poop.errors import PoopError
from poop.interpreter import Interpreter
from poop.transformers.list import ListTransformer, _poop_list, _poop_list_from
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.range import Range
from poop.types.string import Str
from poop.types.tuple import Tuple


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return ListTransformer().transform(tree)


def test_list_literal_is_rewritten() -> None:
    tree = _transform("x = [1, 2, 3]")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_list"
    assert len(call.args) == 3


def test_empty_list_is_rewritten() -> None:
    tree = _transform("x = []")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_list"
    assert len(call.args) == 0


def test_store_context_not_rewritten() -> None:
    tree = _transform("[a, b] = (1, 2)")
    # Assignment target is a List node with Store context — must NOT be rewritten
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    target = assign.targets[0]
    assert isinstance(target, ast.List)


def test_list_call_is_rewritten() -> None:
    tree = _transform("list(x)")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_list_from"


def test_list_call_no_arg_is_rewritten() -> None:
    tree = _transform("list()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_list_from"
    assert len(expr.value.args) == 0


def test_method_named_list_is_not_rewritten() -> None:
    tree = _transform("x.list()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Attribute)
    assert expr.value.func.attr == "list"


def test_bindings_contains_poop_list() -> None:
    assert "_poop_list" in ListTransformer.BINDINGS


def test_bindings_contains_poop_list_from() -> None:
    assert ListTransformer.BINDINGS["_poop_list_from"] is _poop_list_from


def test_poop_list_factory() -> None:
    lst = _poop_list(Int(1), Int(2), Int(3))
    assert isinstance(lst, List)
    assert lst == List(Int(1), Int(2), Int(3))


# _poop_list_from factory tests


def test_list_from_no_arg_returns_empty() -> None:
    result = _poop_list_from()
    assert isinstance(result, List)
    assert result == List()


def test_list_from_list_returns_copy() -> None:
    lst = List(Int(1), Int(2))
    result = _poop_list_from(lst)
    assert result == lst
    assert result is not lst
    result.append(Int(3))
    assert lst == List(Int(1), Int(2))


def test_list_from_tuple() -> None:
    result = _poop_list_from(Tuple(Int(1), Int(2), Int(3)))
    assert isinstance(result, List)
    assert result == List(Int(1), Int(2), Int(3))


def test_list_from_interval() -> None:
    result = _poop_list_from(Range(Int(1), Int(3)))
    assert isinstance(result, List)
    assert result == List(Int(1), Int(2), Int(3))


def test_list_from_str() -> None:
    result = _poop_list_from(Str("abc"))
    assert isinstance(result, List)
    assert result == List(Str("a"), Str("b"), Str("c"))


def test_list_from_bytes() -> None:
    result = _poop_list_from(Bytes(b"\x01\x02"))
    assert isinstance(result, List)
    assert result == List(Int(1), Int(2))


def test_list_from_unsupported_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot convert"):
        _poop_list_from(Int(5))


# Proposal 51. `[*x]`, `(*x,)` and `{*x}` are literals with a spread, and all
# three answered in terms of a constructor call the program never wrote:
# `list() argument after * must be an iterable, not int`.
@pytest.mark.parametrize(
    ("source", "kind"),
    [
        ("[*5]", "list"),
        ("(*5,)", "tuple"),
        ("{*5}", "set"),
    ],
)
def test_a_spread_names_the_literal_the_reader_wrote(source: str, kind: str) -> None:
    with pytest.raises(PoopError) as info:
        Interpreter().run_source(source + "\n")
    message = str(info.value)
    assert f"a {kind} literal can only spread a collection, got an int" in message
    # The two things the old sentence carried and this one must not: a message
    # spelt as a call, and a construct absent from the source.
    assert "()" not in message
    assert "after *" not in message


def test_a_dict_spread_takes_the_mapping_twin() -> None:
    with pytest.raises(PoopError) as info:
        Interpreter().run_source("{**5}\n")
    message = str(info.value)
    assert "a dict literal can only spread a mapping, got an int" in message
    # `** -unpack` carried a stray space, and "dict display" is Python's
    # grammar vocabulary for what POOP calls a literal.
    assert "display" not in message
    assert "-unpack" not in message


@pytest.mark.parametrize(
    "source",
    [
        "xs = [1, 2]\n[*xs, 3].print()",
        "xs = [1, 2]\n(*xs, 3).print()",
        "xs = [1, 2]\n{*xs, 3}.print()",
        'd = {"a": 1}\n{**d, "b": 2}.print()',
        '[*"ab"].print()',
        "[*range(3)].print()",
        '[*{"a": 1}].print()',
    ],
)
def test_a_spread_of_something_iterable_still_works(source: str) -> None:
    Interpreter().run_source(source + "\n")
