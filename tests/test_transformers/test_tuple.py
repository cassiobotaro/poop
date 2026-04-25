import ast

from poop.transformers.tuple import TupleTransformer, _poop_tuple, _poop_tuple_from
from poop.types.int import Int
from poop.types.tuple import Tuple


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return TupleTransformer().transform(tree)


def test_tuple_literal_rewritten() -> None:
    tree = _transform("result = (1, 2, 3)")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_tuple"


def test_tuple_literal_elements() -> None:
    tree = _transform("result = (1, 2)")
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_tuple"
    assert len(call.args) == 2


def test_store_context_preserved() -> None:
    tree = _transform("(a, b) = (1, 2)")
    src = ast.unparse(tree)
    assert "_poop_tuple" not in src or src.count("_poop_tuple") == 1


def test_tuple_call_is_rewritten() -> None:
    tree = _transform("tuple(x)")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_tuple_from"


def test_tuple_call_no_arg_is_rewritten() -> None:
    tree = _transform("tuple()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_tuple_from"
    assert len(expr.value.args) == 0


def test_method_named_tuple_is_not_rewritten() -> None:
    tree = _transform("x.tuple()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Attribute)
    assert expr.value.func.attr == "tuple"


def test_bindings_contain_factory() -> None:
    assert "_poop_tuple" in TupleTransformer.BINDINGS


def test_bindings_contain_tuple_from() -> None:
    assert TupleTransformer.BINDINGS["_poop_tuple_from"] is _poop_tuple_from


def test_poop_tuple_factory() -> None:
    result = _poop_tuple(Int(1), Int(2))
    assert result == Tuple(Int(1), Int(2))


# _poop_tuple_from factory tests


def test_tuple_from_no_arg_returns_empty() -> None:
    result = _poop_tuple_from()
    assert isinstance(result, Tuple)
    assert result == Tuple()


def test_tuple_from_tuple_returns_same() -> None:
    t = Tuple(Int(1), Int(2))
    assert _poop_tuple_from(t) is t


def test_tuple_from_list() -> None:
    from poop.types.list import List

    result = _poop_tuple_from(List(Int(1), Int(2), Int(3)))
    assert isinstance(result, Tuple)
    assert result == Tuple(Int(1), Int(2), Int(3))


def test_tuple_from_interval() -> None:
    from poop.types.interval import Interval

    result = _poop_tuple_from(Interval(Int(1), Int(3)))
    assert isinstance(result, Tuple)
    assert result == Tuple(Int(1), Int(2), Int(3))


def test_tuple_from_str() -> None:
    from poop.types.string import Str

    result = _poop_tuple_from(Str("abc"))
    assert isinstance(result, Tuple)
    assert result == Tuple(Str("a"), Str("b"), Str("c"))


def test_tuple_from_bytes() -> None:
    from poop.types.bytes import Bytes

    result = _poop_tuple_from(Bytes(b"\x01\x02"))
    assert isinstance(result, Tuple)
    assert result == Tuple(Int(1), Int(2))


def test_tuple_from_unsupported_type_raises() -> None:
    import pytest

    with pytest.raises(TypeError, match="cannot convert"):
        _poop_tuple_from(Int(5))
