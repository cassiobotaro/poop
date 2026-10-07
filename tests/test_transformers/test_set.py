from functools import partial

import pytest

from poop.transformers.set import SetTransformer, _poop_set, _poop_set_from
from poop.types.int import Int
from poop.types.list import List
from poop.types.range import Range
from poop.types.set import Set
from poop.types.tuple import Tuple
from tests._support import rewritten

_rewritten = partial(rewritten, SetTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("x = {1, 2, 3}", "x = _poop_set(1, 2, 3)"),
        ("set(x)", "_poop_set_from(x)"),
        ("set()", "_poop_set_from()"),
        ("x.set()", "x.set()"),
    ],
    ids=["literal", "call", "call_no_arg", "method_named_set"],
)
def test_set_rewrite(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


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


def test_set_from_set_returns_copy() -> None:
    s = Set(Int(1), Int(2))
    result = _poop_set_from(s)
    assert result == s
    assert result is not s
    result.add(Int(3))
    assert s == Set(Int(1), Int(2))


def test_set_from_list() -> None:
    result = _poop_set_from(List(Int(1), Int(2), Int(1)))
    assert isinstance(result, Set)
    assert result == Set(Int(1), Int(2))


def test_set_from_interval() -> None:
    result = _poop_set_from(Range(Int(1), Int(3)))
    assert isinstance(result, Set)
    assert result == Set(Int(1), Int(2), Int(3))


def test_set_from_tuple() -> None:
    result = _poop_set_from(Tuple(Int(10), Int(20)))
    assert isinstance(result, Set)
    assert result == Set(Int(10), Int(20))


def test_set_from_unsupported_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot convert"):
        _poop_set_from(Int(5))
