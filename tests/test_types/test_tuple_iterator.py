import pytest

from poop.types.int import Int
from poop.types.tuple import Tuple
from poop.types.tuple_iterator import TupleIterator


def test_iter_returns_tuple_iterator() -> None:
    it = Tuple(Int(1), Int(2)).iter()
    assert isinstance(it, TupleIterator)


def test_next_advances() -> None:
    it = Tuple(Int(10), Int(20)).iter()
    assert it.next() == Int(10)
    assert it.next() == Int(20)


def test_exhaustion_raises_stop_iteration() -> None:
    it = Tuple(Int(1)).iter()
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_one_shot_after_do() -> None:
    it = Tuple(Int(1), Int(2)).iter()
    it.do(lambda x: None)
    with pytest.raises(StopIteration):
        it.next()


def test_iter_is_self() -> None:
    it = Tuple(Int(1)).iter()
    assert iter(it) is it


def test_str_repr() -> None:
    assert str(Tuple().iter()) == "<tuple_iterator>"
