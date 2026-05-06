import pytest

from poop.types.dict_reverse_key_iterator import DictReverseKeyIterator
from poop.types.int import Int
from poop.types.string import Str


def test_next_yields_keys_in_reverse() -> None:
    it = DictReverseKeyIterator(reversed({Str("a"): Int(1), Str("b"): Int(2)}))
    assert it.next() == Str("b")
    assert it.next() == Str("a")


def test_exhaustion_raises_stop_iteration() -> None:
    it = DictReverseKeyIterator(reversed({Str("a"): Int(1)}))
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_iter_returns_self() -> None:
    it = DictReverseKeyIterator(reversed({}))
    assert iter(it) is it


def test_str_repr() -> None:
    assert str(DictReverseKeyIterator(reversed({}))) == "<dict_reversekeyiterator>"
