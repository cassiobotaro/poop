import pytest

from poop.types.str_iterator import StrIterator
from poop.types.string import Str


def test_iter_returns_str_iterator() -> None:
    it = Str("ab").iter()
    assert isinstance(it, StrIterator)


def test_next_yields_str_chars() -> None:
    it = Str("abc").iter()
    assert it.next() == Str("a")
    assert it.next() == Str("b")
    assert it.next() == Str("c")


def test_exhaustion_raises_stop_iteration() -> None:
    it = Str("a").iter()
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_one_shot_after_do() -> None:
    it = Str("ab").iter()
    it.do(lambda x: None)
    with pytest.raises(StopIteration):
        it.next()


def test_iter_is_self() -> None:
    it = Str("a").iter()
    assert iter(it) is it


def test_str_repr() -> None:
    assert str(Str("").iter()) == "<str_iterator>"
