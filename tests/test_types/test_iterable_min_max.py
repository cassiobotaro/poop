"""min/max on iterables.

Mirrors Python's `min(iterable, *, key=None, default=...)`. Lives on
`_IterableMixin` so List, Tuple, Set, FrozenSet, Range, Bytes,
ByteArray, MemoryView, Enumerate, and Zip all get it for free.
"""

from collections.abc import Callable
from typing import Any

import pytest

from poop import Interpreter
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.memory_view import MemoryView
from poop.types.range import Range
from poop.types.set import Set
from poop.types.string import Str
from poop.types.tuple import Tuple


def _ints(*values: int) -> list[Int]:
    return [Int(v) for v in values]


@pytest.mark.parametrize(
    ("factory", "expected_min", "expected_max"),
    [
        (lambda: List(*_ints(3, 1, 4, 1, 5)), Int(1), Int(5)),
        (lambda: Tuple(*_ints(3, 1, 4, 1, 5)), Int(1), Int(5)),
        (lambda: Set(*_ints(3, 1, 4, 5)), Int(1), Int(5)),
        (lambda: FrozenSet(*_ints(3, 1, 4, 5)), Int(1), Int(5)),
        (lambda: Range(Int(2), Int(5), Int(1)), Int(2), Int(5)),
        (lambda: Bytes(b"\x03\x01\x04"), Int(1), Int(4)),
        (lambda: ByteArray(bytearray(b"\x03\x01\x04")), Int(1), Int(4)),
        (lambda: MemoryView(memoryview(b"\x03\x01\x04")), Int(1), Int(4)),
    ],
)
def test_min_max_on_iterable(
    factory: Callable[[], Any], expected_min: Any, expected_max: Any
) -> None:
    iterable = factory()
    assert iterable.min() == expected_min
    assert iterable.max() == expected_max


def test_min_max_with_key() -> None:
    items = List(Str("aa"), Str("b"), Str("ccc"))
    assert items.min(key=lambda s: s.len()) == Str("b")
    assert items.max(key=lambda s: s.len()) == Str("ccc")


def test_min_with_key_returns_original_element_not_key() -> None:
    items = List(Tuple(Int(1), Str("a")), Tuple(Int(0), Str("b")))
    result = items.min(key=lambda pair: pair.at(Int(0)))
    assert result == Tuple(Int(0), Str("b"))


def test_min_max_on_empty_with_default_returns_default() -> None:
    sentinel = Str("empty")
    assert List().min(default=sentinel) is sentinel
    assert List().max(default=sentinel) is sentinel


def test_min_max_on_empty_without_default_raises_value_error() -> None:
    with pytest.raises(ValueError, match="empty"):
        List().min()
    with pytest.raises(ValueError, match="empty"):
        List().max()


def test_min_returns_first_element_on_tie() -> None:
    a = Tuple(Int(0), Str("a"))
    b = Tuple(Int(0), Str("b"))
    items = List(a, b)
    result = items.min(key=lambda t: t.at(Int(0)))
    assert result is a


def test_max_returns_first_element_on_tie() -> None:
    a = Tuple(Int(9), Str("a"))
    b = Tuple(Int(9), Str("b"))
    items = List(a, b)
    result = items.max(key=lambda t: t.at(Int(0)))
    assert result is a


def test_default_none_is_distinguished_from_missing() -> None:
    """default=none should return POOP none, not raise."""
    from poop.types.none import none

    assert List().min(default=none) is none
    assert List().max(default=none) is none


def test_min_end_to_end_via_interpreter() -> None:
    Interpreter().run_source("[3, 1, 4, 1, 5].min().print()")


def test_min_with_key_end_to_end() -> None:
    Interpreter().run_source('["aa", "b", "ccc"].min(key=lambda s: s.len()).print()')


def test_empty_min_via_interpreter_surfaces_value_error() -> None:
    """Inside a Try chain the ValueError surfaces as a POOP Error."""
    Interpreter().run_source(
        "Try(lambda: [].min()).except_(ValueError, lambda e: e.kind().print()).run()"
    )


def test_str_min_returns_smallest_char() -> None:
    assert Str("hello").min() == Str("e")


def test_str_max_returns_largest_char() -> None:
    assert Str("hello").max() == Str("o")


def test_str_min_with_key() -> None:
    assert Str("BAa").min(key=lambda c: c.lower()) == Str("A")


def test_str_min_empty_with_default() -> None:
    assert Str("").min(default=Str("empty!")) == Str("empty!")


def test_str_min_empty_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        Str("").min()
