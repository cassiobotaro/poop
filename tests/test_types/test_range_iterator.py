import pytest

from poop.types.int import Int
from poop.types.range import Range
from poop.types.range_iterator import RangeIterator


def test_iter_returns_range_iterator() -> None:
    it = Range(Int(0), Int(2)).iter()
    assert isinstance(it, RangeIterator)


def test_next_yields_ints() -> None:
    it = Range(Int(0), Int(2)).iter()
    assert it.next() == Int(0)
    assert it.next() == Int(1)
    assert it.next() == Int(2)


def test_exhaustion_raises_stop_iteration() -> None:
    it = Range(Int(0), Int(0)).iter()
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_one_shot_after_do() -> None:
    it = Range(Int(0), Int(2)).iter()
    it.do(lambda x: None)
    with pytest.raises(StopIteration):
        it.next()


def test_iter_is_self() -> None:
    it = Range(Int(0), Int(0)).iter()
    assert iter(it) is it


def test_str_repr() -> None:
    assert str(Range(Int(0), Int(0)).iter()) == "<range_iterator>"
