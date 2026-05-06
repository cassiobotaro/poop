import pytest

from poop.types.int import Int
from poop.types.set import Set
from poop.types.set_iterator import SetIterator


def test_iter_returns_set_iterator() -> None:
    it = Set(Int(1), Int(2)).iter()
    assert isinstance(it, SetIterator)


def test_next_yields_all_elements() -> None:
    s = Set(Int(1), Int(2), Int(3))
    it = s.iter()
    collected: set[Int] = {it.next(), it.next(), it.next()}
    assert collected == {Int(1), Int(2), Int(3)}


def test_exhaustion_raises_stop_iteration() -> None:
    it = Set(Int(1)).iter()
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_one_shot_after_do() -> None:
    it = Set(Int(1), Int(2)).iter()
    it.do(lambda x: None)
    with pytest.raises(StopIteration):
        it.next()


def test_iter_is_self() -> None:
    it = Set(Int(1)).iter()
    assert iter(it) is it


def test_str_repr() -> None:
    assert str(Set().iter()) == "<set_iterator>"
