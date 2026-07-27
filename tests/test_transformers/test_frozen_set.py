import ast

import pytest

from poop.transformers.frozen_set import (
    FrozenSetTransformer,
    _poop_frozenset_from,
)
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.range import Range
from poop.types.tuple import Tuple


def _transform(source: str) -> ast.Module:
    tree = ast.parse(source)
    return FrozenSetTransformer().transform(tree)


def test_frozenset_call_is_rewritten() -> None:
    tree = _transform("frozenset(x)")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_frozenset_from"


def test_frozenset_call_no_arg_is_rewritten() -> None:
    tree = _transform("frozenset()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Name)
    assert expr.value.func.id == "_poop_frozenset_from"
    assert len(expr.value.args) == 0


def test_method_named_frozenset_is_not_rewritten() -> None:
    tree = _transform("x.frozenset()")
    expr = tree.body[0]
    assert isinstance(expr, ast.Expr)
    assert isinstance(expr.value, ast.Call)
    assert isinstance(expr.value.func, ast.Attribute)
    assert expr.value.func.attr == "frozenset"


def test_bindings_contains_poop_frozenset_from() -> None:
    assert FrozenSetTransformer.BINDINGS["_poop_frozenset_from"] is _poop_frozenset_from


def test_frozenset_from_no_arg_returns_empty() -> None:
    result = _poop_frozenset_from()
    assert isinstance(result, FrozenSet)
    assert result == FrozenSet()


def test_frozenset_from_frozenset_returns_same() -> None:
    fs = FrozenSet(Int(1), Int(2))
    result = _poop_frozenset_from(fs)
    assert result is fs


def test_frozenset_from_list() -> None:
    result = _poop_frozenset_from(List(Int(1), Int(2), Int(1)))
    assert isinstance(result, FrozenSet)
    assert result == FrozenSet(Int(1), Int(2))


def test_frozenset_from_interval() -> None:
    result = _poop_frozenset_from(Range(Int(1), Int(3)))
    assert isinstance(result, FrozenSet)
    assert result == FrozenSet(Int(1), Int(2), Int(3))


def test_frozenset_from_tuple() -> None:
    result = _poop_frozenset_from(Tuple(Int(10), Int(20)))
    assert isinstance(result, FrozenSet)
    assert result == FrozenSet(Int(10), Int(20))


def test_frozenset_from_unsupported_type_raises_clean_message() -> None:
    # Regression: a non-iterable used to leak Python's raw type name and the
    # internal "argument after * must be an iterable" wording; it must now
    # match set/list/tuple's "cannot convert int to frozenset".
    with pytest.raises(TypeError, match="cannot convert int to frozenset"):
        _poop_frozenset_from(Int(5))
