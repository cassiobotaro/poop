import pytest

from poop.types.frozen_set import FrozenSet
from poop.types.frozen_set_iterator import FrozenSetIterator
from poop.types.int import Int
from poop.types.object import Object


def test_iter_returns_frozen_set_iterator() -> None:
    it = FrozenSet(Int(1), Int(2)).iter()
    assert isinstance(it, FrozenSetIterator)


def test_next_yields_all_elements() -> None:
    s = FrozenSet(Int(1), Int(2), Int(3))
    it = s.iter()
    collected: set[Object] = {it.next(), it.next(), it.next()}
    assert collected == {Int(1), Int(2), Int(3)}


def test_exhaustion_raises_stop_iteration() -> None:
    it = FrozenSet(Int(1)).iter()
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_one_shot_after_do() -> None:
    it = FrozenSet(Int(1), Int(2)).iter()
    it.do(lambda x: None)
    with pytest.raises(StopIteration):
        it.next()


def test_iter_is_self() -> None:
    it = FrozenSet(Int(1)).iter()
    assert iter(it) is it


def test_str_repr() -> None:
    assert str(FrozenSet().iter()) == "<set_iterator>"
