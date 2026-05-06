import pytest

from poop.types.dict_reverse_value_iterator import DictReverseValueIterator
from poop.types.int import Int


def test_next_yields_values_in_reverse() -> None:
    d = {"a": Int(1), "b": Int(2)}
    it = DictReverseValueIterator(reversed(list(d.values())))
    assert it.next() == Int(2)
    assert it.next() == Int(1)


def test_exhaustion_raises_stop_iteration() -> None:
    it = DictReverseValueIterator(iter([Int(1)]))
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_iter_returns_self() -> None:
    it = DictReverseValueIterator(iter([]))
    assert iter(it) is it


def test_str_repr() -> None:
    assert str(DictReverseValueIterator(iter([]))) == "<dict_reversevalueiterator>"
