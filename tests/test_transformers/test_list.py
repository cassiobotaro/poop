import ast

from poop.transformers.list import ListTransformer, _poop_list, _poop_list_from
from poop.types.int import Int
from poop.types.list import List


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


def test_list_from_list_returns_same() -> None:
    lst = List(Int(1), Int(2))
    assert _poop_list_from(lst) is lst


def test_list_from_tuple() -> None:
    from poop.types.tuple import Tuple

    result = _poop_list_from(Tuple(Int(1), Int(2), Int(3)))
    assert isinstance(result, List)
    assert result == List(Int(1), Int(2), Int(3))


def test_list_from_interval() -> None:
    from poop.types.interval import Interval

    result = _poop_list_from(Interval(Int(1), Int(3)))
    assert isinstance(result, List)
    assert result == List(Int(1), Int(2), Int(3))


def test_list_from_str() -> None:
    from poop.types.string import Str

    result = _poop_list_from(Str("abc"))
    assert isinstance(result, List)
    assert result == List(Str("a"), Str("b"), Str("c"))


def test_list_from_bytes() -> None:
    from poop.types.bytes import Bytes

    result = _poop_list_from(Bytes(b"\x01\x02"))
    assert isinstance(result, List)
    assert result == List(Int(1), Int(2))


def test_list_from_unsupported_type_raises() -> None:
    import pytest

    with pytest.raises(TypeError, match="cannot convert"):
        _poop_list_from(Int(5))
