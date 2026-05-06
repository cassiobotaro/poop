import pytest

from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.dict_key_iterator import DictKeyIterator
from poop.types.dict_keys import DictKeys
from poop.types.dict_reverse_key_iterator import DictReverseKeyIterator
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.mapping_proxy import MappingProxy
from poop.types.set import Set
from poop.types.string import Str


def _make() -> Dict:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    d.at_put(Str("b"), Int(2))
    return d


def test_iter_returns_dict_key_iterator() -> None:
    keys = DictKeys(_make())
    assert isinstance(keys.iter(), DictKeyIterator)


def test_iter_yields_keys() -> None:
    keys = DictKeys(_make())
    it = keys.iter()
    assert it.next() == Str("a")
    assert it.next() == Str("b")


def test_len() -> None:
    keys = DictKeys(_make())
    assert keys.len() == Int(2)
    assert len(keys) == 2


def test_contains() -> None:
    keys = DictKeys(_make())
    assert keys.includes(Str("a")) is true
    assert keys.includes(Str("missing")) is false
    assert Str("a") in keys
    assert Str("missing") not in keys


def test_reversed() -> None:
    keys = DictKeys(_make())
    rev = keys.reversed()
    assert isinstance(rev, DictReverseKeyIterator)
    assert rev.next() == Str("b")
    assert rev.next() == Str("a")


def test_isdisjoint_set() -> None:
    keys = DictKeys(_make())
    assert keys.isdisjoint(Set(Str("x"))) is true
    assert keys.isdisjoint(Set(Str("a"))) is false


def test_isdisjoint_dict_keys() -> None:
    keys = DictKeys(_make())
    other = Dict()
    other.at_put(Str("x"), Int(0))
    assert keys.isdisjoint(DictKeys(other)) is true


def test_mapping() -> None:
    keys = DictKeys(_make())
    mp = keys.mapping()
    assert isinstance(mp, MappingProxy)
    assert mp.at(Str("a")) == Int(1)


def test_list_escape() -> None:
    from poop.transformers.list import _poop_list_from

    keys = DictKeys(_make())
    lst = _poop_list_from(keys)
    assert isinstance(lst, List)
    assert lst == List(Str("a"), Str("b"))


def test_or_returns_set() -> None:
    keys = DictKeys(_make())
    other = Set(Str("c"))
    result = keys | other
    assert isinstance(result, Set)
    assert {x for x in result._data} == {Str("a"), Str("b"), Str("c")}


def test_and_returns_set() -> None:
    keys = DictKeys(_make())
    result = keys & Set(Str("a"), Str("x"))
    assert result._data == {Str("a")}


def test_sub_returns_set() -> None:
    keys = DictKeys(_make())
    result = keys - Set(Str("a"))
    assert result._data == {Str("b")}


def test_xor_returns_set() -> None:
    keys = DictKeys(_make())
    result = keys ^ Set(Str("b"), Str("c"))
    assert result._data == {Str("a"), Str("c")}


def test_eq_with_dict_keys() -> None:
    a = DictKeys(_make())
    b = DictKeys(_make())
    assert (a == b) is true


def test_eq_with_set() -> None:
    keys = DictKeys(_make())
    assert (keys == Set(Str("a"), Str("b"))) is true
    assert (keys == Set(Str("a"))) is false


def test_eq_with_frozen_set() -> None:
    keys = DictKeys(_make())
    assert (keys == FrozenSet(Str("a"), Str("b"))) is true


def test_le_lt_ge_gt() -> None:
    keys = DictKeys(_make())  # {a, b}
    assert (keys <= Set(Str("a"), Str("b"), Str("c"))) is true
    assert (keys < Set(Str("a"), Str("b"), Str("c"))) is true
    assert (keys < Set(Str("a"), Str("b"))) is false
    assert (keys >= Set(Str("a"))) is true
    assert (keys > Set(Str("a"))) is true
    assert (keys > Set(Str("a"), Str("b"))) is false


def test_liveness() -> None:
    d = _make()
    keys = DictKeys(d)
    assert keys.len() == Int(2)
    d.at_put(Str("c"), Int(3))
    assert keys.len() == Int(3)
    assert keys.includes(Str("c")) is true


def test_iterable_mixin_do() -> None:
    keys = DictKeys(_make())
    seen: list[Str] = []
    keys.do(lambda k: seen.append(k))
    assert seen == [Str("a"), Str("b")]


def test_str_repr() -> None:
    keys = DictKeys(_make())
    assert str(keys) == "dict_keys(['a', 'b'])"


def test_unhashable() -> None:
    with pytest.raises(TypeError):
        hash(DictKeys(_make()))


def test_reflected_or() -> None:
    keys = DictKeys(_make())
    result = Set(Str("c")) | keys
    assert result._data == {Str("a"), Str("b"), Str("c")}


def test_reflected_and() -> None:
    keys = DictKeys(_make())
    result = Set(Str("a"), Str("x")) & keys
    assert result._data == {Str("a")}


def test_reflected_sub() -> None:
    keys = DictKeys(_make())
    result = Set(Str("a"), Str("x")) - keys
    assert result._data == {Str("x")}


def test_reflected_xor() -> None:
    keys = DictKeys(_make())
    result = Set(Str("b"), Str("c")) ^ keys
    assert result._data == {Str("a"), Str("c")}


def test_eq_with_other_type() -> None:
    keys = DictKeys(_make())
    assert (keys == Int(0)) is false


def test_ne() -> None:
    a = DictKeys(_make())
    b = DictKeys(Dict())
    assert (a != b) is true
    assert (a != a) is false


def test_other_keys_passthrough() -> None:
    # When other is a raw Python set, _other_keys returns it as-is
    keys = DictKeys(_make())
    result = keys.isdisjoint(set())
    assert result is true


def test_reversed_dunder() -> None:
    keys = DictKeys(_make())
    assert list(reversed(keys))[0] == Str("b")
