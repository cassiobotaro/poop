import ast

import pytest

from poop.transformers.dict import (
    DictTransformer,
    _poop_dict_from,
    _poop_dict_from_pairs,
)
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.string import Str


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return DictTransformer().transform(tree)


def test_dict_literal_is_rewritten() -> None:
    tree = _transform('x = {"a": 1}')
    assign = tree.body[0]
    assert isinstance(assign, ast.Assign)
    call = assign.value
    assert isinstance(call, ast.Call)
    assert isinstance(call.func, ast.Name)
    assert call.func.id == "_poop_dict_from_pairs"
    assert len(call.args) == 2


def test_dict_call_is_rewritten() -> None:
    tree = _transform("dict(x)")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_dict_from"


def test_dict_call_no_arg_is_rewritten() -> None:
    tree = _transform("dict()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_dict_from"
    assert len(expr.value.args) == 0


def test_method_named_dict_is_not_rewritten() -> None:
    tree = _transform("x.dict()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Attribute)
    assert expr.value.func.attr == "dict"


def test_bindings_contains_poop_dict_from_pairs() -> None:
    assert "_poop_dict_from_pairs" in DictTransformer.BINDINGS


def test_bindings_contains_poop_dict_from() -> None:
    assert DictTransformer.BINDINGS["_poop_dict_from"] is _poop_dict_from


def test_poop_dict_from_pairs_factory() -> None:
    result = _poop_dict_from_pairs(Str("a"), Int(1), Str("b"), Int(2))
    assert isinstance(result, Dict)
    expected = Dict()
    expected._data[Str("a")] = Int(1)
    expected._data[Str("b")] = Int(2)
    assert result == expected


# _poop_dict_from factory tests


def test_dict_from_no_arg_returns_empty() -> None:
    result = _poop_dict_from()
    assert isinstance(result, Dict)
    assert result == Dict()


def test_dict_from_dict_returns_same() -> None:
    d = Dict()
    d._data[Str("x")] = Int(1)
    assert _poop_dict_from(d) is d


def test_dict_from_list_of_tuples() -> None:
    from poop.types.list import List
    from poop.types.tuple import Tuple

    pairs = List(Tuple(Str("a"), Int(1)), Tuple(Str("b"), Int(2)))
    result = _poop_dict_from(pairs)
    assert isinstance(result, Dict)
    assert result.at(Str("a")) == Int(1)
    assert result.at(Str("b")) == Int(2)


def test_dict_from_tuple_of_tuples() -> None:
    from poop.types.tuple import Tuple

    pairs = Tuple(Tuple(Str("x"), Int(10)), Tuple(Str("y"), Int(20)))
    result = _poop_dict_from(pairs)
    assert isinstance(result, Dict)
    assert result.at(Str("x")) == Int(10)
    assert result.at(Str("y")) == Int(20)


def test_dict_from_entry_wrong_size_raises() -> None:
    from poop.types.list import List
    from poop.types.tuple import Tuple

    with pytest.raises(TypeError):
        _poop_dict_from(List(Tuple(Str("a"), Int(1), Int(2))))
