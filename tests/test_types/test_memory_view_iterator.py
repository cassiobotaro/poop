import pytest

from poop.types.int import Int
from poop.types.memory_view import MemoryView
from poop.types.memory_view_iterator import MemoryViewIterator


def test_iter_returns_memory_view_iterator() -> None:
    it = MemoryView(memoryview(b"ab")).iter()
    assert isinstance(it, MemoryViewIterator)


def test_next_yields_ints() -> None:
    it = MemoryView(memoryview(b"abc")).iter()
    assert it.next() == Int(ord("a"))
    assert it.next() == Int(ord("b"))
    assert it.next() == Int(ord("c"))


def test_exhaustion_raises_stop_iteration() -> None:
    it = MemoryView(memoryview(b"a")).iter()
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_one_shot_after_do() -> None:
    it = MemoryView(memoryview(b"ab")).iter()
    it.do(lambda x: None)
    with pytest.raises(StopIteration):
        it.next()


def test_iter_is_self() -> None:
    it = MemoryView(memoryview(b"a")).iter()
    assert iter(it) is it


def test_str_repr() -> None:
    assert str(MemoryView(memoryview(b"")).iter()) == "<memory_iterator>"
