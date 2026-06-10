import pytest

from poop.types.int import Int
from poop.types.list import List
from poop.types.list_iterator import ListIterator
from poop.types.string import Str


def test_iter_returns_list_iterator() -> None:
    it = List(Int(1), Int(2)).iter()
    assert isinstance(it, ListIterator)


def test_class_name_answers_list_iterator() -> None:
    assert List(Int(1)).iter().class_name() == Str("list_iterator")


def test_next_advances() -> None:
    it = List(Int(10), Int(20)).iter()
    assert it.next() == Int(10)
    assert it.next() == Int(20)


def test_exhaustion_raises_stop_iteration() -> None:
    it = List(Int(1)).iter()
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_one_shot_after_do() -> None:
    it = List(Int(1), Int(2)).iter()
    it.do(lambda x: None)
    with pytest.raises(StopIteration):
        it.next()


def test_iter_is_self() -> None:
    it = List(Int(1)).iter()
    assert iter(it) is it


def test_str_repr() -> None:
    assert str(List().iter()) == "<list_iterator>"
