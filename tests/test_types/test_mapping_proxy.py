import pytest

from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.mapping_proxy import MappingProxy
from poop.types.none import none
from poop.types.string import Str


def _make() -> Dict:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    d.at_put(Str("b"), Int(2))
    return d


def test_at() -> None:
    mp = MappingProxy(_make())
    assert mp.at(Str("a")) == Int(1)


def test_at_missing_raises() -> None:
    mp = MappingProxy(Dict())
    with pytest.raises(KeyError):
        mp.at(Str("x"))


def test_get_default() -> None:
    mp = MappingProxy(_make())
    assert mp.get(Str("a")) == Int(1)
    assert mp.get(Str("missing")) is none
    assert mp.get(Str("missing"), Int(99)) == Int(99)


def test_includes() -> None:
    mp = MappingProxy(_make())
    assert mp.includes(Str("a")) is true
    assert mp.includes(Str("missing")) is false


def test_len() -> None:
    mp = MappingProxy(_make())
    assert mp.len() == Int(2)
    assert len(mp) == 2


def test_contains_dunder() -> None:
    mp = MappingProxy(_make())
    assert Str("a") in mp
    assert Str("missing") not in mp


def test_iter_yields_keys() -> None:
    mp = MappingProxy(_make())
    assert list(iter(mp)) == [Str("a"), Str("b")]


def test_reversed() -> None:
    mp = MappingProxy(_make())
    rev = mp.reversed()
    assert rev.next() == Str("b")
    assert rev.next() == Str("a")


def test_copy_returns_dict() -> None:
    mp = MappingProxy(_make())
    cp = mp.copy()
    assert isinstance(cp, Dict)
    assert cp.at(Str("a")) == Int(1)


def test_liveness() -> None:
    d = _make()
    mp = MappingProxy(d)
    d.at_put(Str("c"), Int(3))
    assert mp.len() == Int(3)
    assert mp.at(Str("c")) == Int(3)


def test_no_mutation_methods() -> None:
    mp = MappingProxy(_make())
    assert not hasattr(mp, "at_put")
    assert not hasattr(mp, "clear")
    assert not hasattr(mp, "pop")


def test_eq_with_mapping_proxy() -> None:
    a = MappingProxy(_make())
    b = MappingProxy(_make())
    assert (a == b) is true


def test_eq_with_dict() -> None:
    mp = MappingProxy(_make())
    other = _make()
    assert (mp == other) is true


def test_or_returns_dict() -> None:
    a = MappingProxy(_make())
    b_dict = Dict()
    b_dict.at_put(Str("c"), Int(3))
    b = MappingProxy(b_dict)
    merged = a | b
    assert isinstance(merged, Dict)
    assert merged.at(Str("a")) == Int(1)
    assert merged.at(Str("c")) == Int(3)


def test_str_repr() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    mp = MappingProxy(d)
    assert str(mp) == "mappingproxy({'a': 1})"


def test_unhashable() -> None:
    mp = MappingProxy(Dict())
    with pytest.raises(TypeError):
        hash(mp)


def test_keys_returns_dict_keys() -> None:
    from poop.types.dict_keys import DictKeys

    mp = MappingProxy(_make())
    assert isinstance(mp.keys(), DictKeys)


def test_values_returns_dict_values() -> None:
    from poop.types.dict_values import DictValues

    mp = MappingProxy(_make())
    assert isinstance(mp.values(), DictValues)


def test_items_returns_dict_items() -> None:
    from poop.types.dict_items import DictItems

    mp = MappingProxy(_make())
    assert isinstance(mp.items(), DictItems)


def test_iter_method_returns_dict_key_iterator() -> None:
    from poop.types.dict_key_iterator import DictKeyIterator

    mp = MappingProxy(_make())
    assert isinstance(mp.iter(), DictKeyIterator)


def test_reversed_dunder() -> None:
    mp = MappingProxy(_make())
    assert list(reversed(mp)) == [Str("b"), Str("a")]


def test_eq_with_other_type() -> None:
    mp = MappingProxy(_make())
    assert (mp == Int(0)) is false


def test_ne_with_dict_proxy() -> None:
    a = MappingProxy(_make())
    b = MappingProxy(Dict())
    assert (a != b) is true
    assert (a != a) is false
