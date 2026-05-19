import pytest

from poop.types.dict import Dict
from poop.types.dict_key_iterator import DictKeyIterator
from poop.types.int import Int
from poop.types.object import Object
from poop.types.string import Str


def test_iter_returns_dict_key_iterator() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    assert isinstance(d.iter(), DictKeyIterator)


def test_next_yields_keys() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    d.at_put(Str("b"), Int(2))
    it = d.iter()
    collected: set[Object] = {it.next(), it.next()}
    assert collected == {Str("a"), Str("b")}


def test_exhaustion_raises_stop_iteration() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    it = d.iter()
    it.next()
    with pytest.raises(StopIteration):
        it.next()


def test_one_shot_after_do() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    d.at_put(Str("b"), Int(2))
    it = d.iter()
    it.do(lambda x: None)
    with pytest.raises(StopIteration):
        it.next()


def test_iter_is_self() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    it = d.iter()
    assert iter(it) is it


def test_str_repr() -> None:
    assert str(Dict().iter()) == "<dict_keyiterator>"
