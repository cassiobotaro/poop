import ast

from poop.transformers.set import SetTransformer, _poop_set, _poop_set_from
from poop.types.int import Int
from poop.types.set import Set


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return SetTransformer().transform(tree)


def test_set_literal_is_rewritten() -> None:
    tree = _transform("x = {1, 2, 3}")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_set"
    assert len(call.args) == 3


def test_set_call_is_rewritten() -> None:
    tree = _transform("set(x)")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_set_from"


def test_set_call_no_arg_is_rewritten() -> None:
    tree = _transform("set()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_set_from"
    assert len(expr.value.args) == 0


def test_method_named_set_is_not_rewritten() -> None:
    tree = _transform("x.set()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Attribute)
    assert expr.value.func.attr == "set"


def test_bindings_contains_poop_set() -> None:
    assert "_poop_set" in SetTransformer.BINDINGS


def test_bindings_contains_poop_set_from() -> None:
    assert SetTransformer.BINDINGS["_poop_set_from"] is _poop_set_from


def test_poop_set_factory() -> None:
    result = _poop_set(Int(1), Int(2))
    assert isinstance(result, Set)


# _poop_set_from factory tests


def test_set_from_no_arg_returns_empty() -> None:
    result = _poop_set_from()
    assert isinstance(result, Set)
    assert result == Set()


def test_set_from_set_returns_same() -> None:
    s = Set(Int(1), Int(2))
    assert _poop_set_from(s) is s


def test_set_from_list() -> None:
    from poop.types.list import List

    result = _poop_set_from(List(Int(1), Int(2), Int(1)))
    assert isinstance(result, Set)
    assert result == Set(Int(1), Int(2))


def test_set_from_interval() -> None:
    from poop.types.interval import Interval

    result = _poop_set_from(Interval(Int(1), Int(3)))
    assert isinstance(result, Set)
    assert result == Set(Int(1), Int(2), Int(3))


def test_set_from_tuple() -> None:
    from poop.types.tuple import Tuple

    result = _poop_set_from(Tuple(Int(10), Int(20)))
    assert isinstance(result, Set)
    assert result == Set(Int(10), Int(20))
