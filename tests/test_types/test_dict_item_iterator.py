import pytest

from poop.types.dict_item_iterator import DictItemIterator
from poop.types.int import Int
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_next_yields_tuples() -> None:
    pairs = [(Str("a"), Int(1)), (Str("b"), Int(2))]
    it = DictItemIterator(pairs)
    assert it.next() == Tuple(Str("a"), Int(1))
    assert it.next() == Tuple(Str("b"), Int(2))


def test_exhaustion_raises_stop_iteration() -> None:
    it = DictItemIterator([(Str("a"), Int(1))])
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_next_default_on_exhaustion() -> None:
    it = DictItemIterator([(Str("a"), Int(1))])
    it.next()
    fallback = Tuple(Str("end"), Int(0))
    assert it.next(fallback) is fallback


def test_iter_returns_self() -> None:
    it = DictItemIterator([])
    assert iter(it) is it


def test_do_yields_tuples() -> None:
    pairs = [(Str("a"), Int(1)), (Str("b"), Int(2))]
    it = DictItemIterator(pairs)
    seen: list[Tuple] = []
    it.do(lambda t: seen.append(t))
    assert seen == [Tuple(Str("a"), Int(1)), Tuple(Str("b"), Int(2))]


def test_one_shot_after_do() -> None:
    it = DictItemIterator([(Str("a"), Int(1))])
    it.do(lambda t: None)
    with pytest.raises(StopIteration):
        it.next()


def test_str_repr() -> None:
    assert str(DictItemIterator([])) == "<dict_itemiterator>"
