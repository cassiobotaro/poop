import pytest

from poop.types.dict_reverse_item_iterator import DictReverseItemIterator
from poop.types.int import Int
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_next_yields_tuples_in_reverse() -> None:
    pairs = [(Str("b"), Int(2)), (Str("a"), Int(1))]  # already reversed
    it = DictReverseItemIterator(pairs)
    assert it.next() == Tuple(Str("b"), Int(2))
    assert it.next() == Tuple(Str("a"), Int(1))


def test_exhaustion_raises_stop_iteration() -> None:
    it = DictReverseItemIterator([(Str("a"), Int(1))])
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_iter_returns_self() -> None:
    it = DictReverseItemIterator([])
    assert iter(it) is it


def test_do_yields_tuples() -> None:
    pairs = [(Str("b"), Int(2)), (Str("a"), Int(1))]
    it = DictReverseItemIterator(pairs)
    seen: list[Tuple] = []
    it.do(lambda t: seen.append(t))
    assert seen == [Tuple(Str("b"), Int(2)), Tuple(Str("a"), Int(1))]


def test_str_repr() -> None:
    assert str(DictReverseItemIterator([])) == "<dict_reverseitemiterator>"
