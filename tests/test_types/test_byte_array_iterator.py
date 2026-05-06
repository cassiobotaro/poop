import pytest

from poop.types.byte_array import ByteArray
from poop.types.byte_array_iterator import ByteArrayIterator
from poop.types.int import Int


def test_iter_returns_byte_array_iterator() -> None:
    it = ByteArray(bytearray(b"ab")).iter()
    assert isinstance(it, ByteArrayIterator)


def test_next_yields_ints() -> None:
    it = ByteArray(bytearray(b"abc")).iter()
    assert it.next() == Int(ord("a"))
    assert it.next() == Int(ord("b"))
    assert it.next() == Int(ord("c"))


def test_exhaustion_raises_stop_iteration() -> None:
    it = ByteArray(bytearray(b"a")).iter()
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_one_shot_after_do() -> None:
    it = ByteArray(bytearray(b"ab")).iter()
    it.do(lambda x: None)
    with pytest.raises(StopIteration):
        it.next()


def test_iter_is_self() -> None:
    it = ByteArray(bytearray(b"a")).iter()
    assert iter(it) is it


def test_str_repr() -> None:
    assert str(ByteArray(bytearray(b"")).iter()) == "<bytearray_iterator>"
