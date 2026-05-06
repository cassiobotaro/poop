import pytest

from poop.types.bytes import Bytes
from poop.types.bytes_iterator import BytesIterator
from poop.types.int import Int


def test_iter_returns_bytes_iterator() -> None:
    it = Bytes(b"ab").iter()
    assert isinstance(it, BytesIterator)


def test_next_yields_ints() -> None:
    it = Bytes(b"abc").iter()
    assert it.next() == Int(ord("a"))
    assert it.next() == Int(ord("b"))
    assert it.next() == Int(ord("c"))


def test_exhaustion_raises_stop_iteration() -> None:
    it = Bytes(b"a").iter()
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_one_shot_after_do() -> None:
    it = Bytes(b"ab").iter()
    it.do(lambda x: None)
    with pytest.raises(StopIteration):
        it.next()


def test_iter_is_self() -> None:
    it = Bytes(b"a").iter()
    assert iter(it) is it


def test_str_repr() -> None:
    assert str(Bytes(b"").iter()) == "<bytes_iterator>"
