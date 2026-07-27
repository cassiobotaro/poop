import pytest

from poop.types._iterator_base import _IteratorBase
from poop.types.exceptions import MIRRORS
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none


def test_next_advances() -> None:
    it = _IteratorBase([Int(1), Int(2), Int(3)])
    assert it.next() == Int(1)
    assert it.next() == Int(2)
    assert it.next() == Int(3)


def test_next_raises_on_exhaustion() -> None:
    it = _IteratorBase([Int(1)])
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_iter_returns_self() -> None:
    it = _IteratorBase([Int(1)])
    assert iter(it) is it


def test_dunder_next() -> None:
    it = _IteratorBase([Int(7)])
    assert next(it) == Int(7)
    with pytest.raises(StopIteration):
        next(it)


def test_do_consumes_remaining() -> None:
    it = _IteratorBase([Int(1), Int(2), Int(3)])
    it.next()
    collected: list[Int] = []
    result = it.do(lambda x: collected.append(x))
    assert collected == [Int(2), Int(3)]
    assert result is none


def test_do_on_exhausted_is_noop() -> None:
    it = _IteratorBase([Int(1)])
    it.next()
    collected: list[Int] = []
    result = it.do(lambda x: collected.append(x))
    assert collected == []
    assert result is none


def test_one_shot_invariant() -> None:
    it = _IteratorBase([Int(1), Int(2)])
    it.do(lambda x: None)
    with pytest.raises(StopIteration):
        it.next()


# An iterator is an iterable, so — like any POOP iterable — it answers the full
# `_IterableMixin` protocol, not just `next`/`do`. This mirrors Python, where an
# iterator is a valid argument to `filter`/`map`/`enumerate`/`reduce`/...


def test_map_is_understood() -> None:
    it = _IteratorBase([Int(1), Int(2), Int(3)])
    assert list(it.map(lambda x: Int(x._value * 10))) == [Int(10), Int(20), Int(30)]


def test_filter_is_understood() -> None:
    it = _IteratorBase([Int(1), Int(2), Int(3), Int(4)])
    assert list(it.filter(lambda x: x._value % 2 == 0)) == [Int(2), Int(4)]


def test_find_is_understood() -> None:
    it = _IteratorBase([Int(1), Int(2), Int(3)])
    assert it.find(lambda x: x._value == 2) == Int(2)


def test_reduce_is_understood() -> None:
    it = _IteratorBase([Int(1), Int(2), Int(3)])
    assert it.reduce(Int(0), lambda a, b: Int(a._value + b._value)) == Int(6)


def test_enumerate_is_understood() -> None:
    from poop.types.tuple import Tuple

    it = _IteratorBase([Int(5), Int(6)])
    assert list(it.enumerate()) == [
        Tuple(Int(0), Int(5)),
        Tuple(Int(1), Int(6)),
    ]


def test_protocol_message_consumes_iterator() -> None:
    # A consuming message drains the one-shot iterator, matching Python.
    it = _IteratorBase([Int(1), Int(2), Int(3)])
    it.find(lambda x: x._value == 2)
    assert it.next() == Int(3)


def test_exhaustion_carries_a_sentence_naming_the_iterator() -> None:
    # The native StopIteration carries no message at all, so `_describe`
    # degraded to the bare class name: a word naming the CPython protocol
    # that drives `for`, with nothing to say what went wrong.
    it = List(Int(1)).iter()
    it.next()
    with pytest.raises(
        StopIteration,
        match=r"^list_iterator is exhausted — send #next with a default",
    ):
        it.next()


def test_exhaustion_is_still_catchable_as_stop_iteration() -> None:
    # It stays in _HIERARCHY precisely so a Try can catch it.
    it = List().iter()
    with pytest.raises(MIRRORS["StopIteration"]):
        it.next()


def test_a_default_still_answers_instead_of_raising() -> None:
    assert List().iter().next(Int(0)) == Int(0)
