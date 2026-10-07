from functools import partial

import pytest

from poop.transformers.tuple import TupleTransformer, _poop_tuple, _poop_tuple_from
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.range import Range
from poop.types.string import Str
from poop.types.tuple import Tuple
from tests._support import rewritten

_rewritten = partial(rewritten, TupleTransformer())


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("result = (1, 2, 3)", "result = _poop_tuple(1, 2, 3)"),
        ("result = (1, 2)", "result = _poop_tuple(1, 2)"),
        # The Store-context target stays a plain tuple; only the value wraps.
        ("(a, b) = (1, 2)", "a, b = _poop_tuple(1, 2)"),
        ("tuple(x)", "_poop_tuple_from(x)"),
        ("tuple()", "_poop_tuple_from()"),
        ("x.tuple()", "x.tuple()"),
    ],
    ids=[
        "literal",
        "literal_elements",
        "store_context_preserved",
        "call",
        "call_no_arg",
        "method_named_tuple",
    ],
)
def test_tuple_rewrite(source: str, expected: str) -> None:
    assert _rewritten(source) == expected


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
    result = _poop_tuple_from(List(Int(1), Int(2), Int(3)))
    assert isinstance(result, Tuple)
    assert result == Tuple(Int(1), Int(2), Int(3))


def test_tuple_from_interval() -> None:
    result = _poop_tuple_from(Range(Int(1), Int(3)))
    assert isinstance(result, Tuple)
    assert result == Tuple(Int(1), Int(2), Int(3))


def test_tuple_from_str() -> None:
    result = _poop_tuple_from(Str("abc"))
    assert isinstance(result, Tuple)
    assert result == Tuple(Str("a"), Str("b"), Str("c"))


def test_tuple_from_bytes() -> None:
    result = _poop_tuple_from(Bytes(b"\x01\x02"))
    assert isinstance(result, Tuple)
    assert result == Tuple(Int(1), Int(2))


def test_tuple_from_unsupported_type_raises() -> None:
    with pytest.raises(TypeError, match="cannot convert"):
        _poop_tuple_from(Int(5))
