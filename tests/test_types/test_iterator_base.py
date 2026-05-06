import pytest

from poop.types._iterator_base import _IteratorBase
from poop.types.int import Int
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
