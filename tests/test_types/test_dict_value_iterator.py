import pytest

from poop.types.dict_value_iterator import DictValueIterator
from poop.types.int import Int


def test_next_yields_values() -> None:
    it = DictValueIterator([Int(1), Int(2), Int(3)])
    assert it.next() == Int(1)
    assert it.next() == Int(2)
    assert it.next() == Int(3)


def test_exhaustion_raises_stop_iteration() -> None:
    it = DictValueIterator([Int(1)])
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_iter_returns_self() -> None:
    it = DictValueIterator([Int(1)])
    assert iter(it) is it


def test_one_shot_after_do() -> None:
    it = DictValueIterator([Int(1), Int(2)])
    it.do(lambda x: None)
    with pytest.raises(StopIteration):
        it.next()


def test_str_repr() -> None:
    assert str(DictValueIterator([])) == "<dict_valueiterator>"
