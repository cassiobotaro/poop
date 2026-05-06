import pytest

from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.dict_item_iterator import DictItemIterator
from poop.types.dict_items import DictItems
from poop.types.dict_reverse_item_iterator import DictReverseItemIterator
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.mapping_proxy import MappingProxy
from poop.types.set import Set
from poop.types.string import Str
from poop.types.tuple import Tuple


def _make() -> Dict:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    d.at_put(Str("b"), Int(2))
    return d


def test_iter_returns_dict_item_iterator() -> None:
    items = DictItems(_make())
    assert isinstance(items.iter(), DictItemIterator)


def test_iter_yields_tuples() -> None:
    items = DictItems(_make())
    it = items.iter()
    assert it.next() == Tuple(Str("a"), Int(1))
    assert it.next() == Tuple(Str("b"), Int(2))


def test_len() -> None:
    items = DictItems(_make())
    assert items.len() == Int(2)
    assert len(items) == 2


def test_contains() -> None:
    items = DictItems(_make())
    assert items.includes(Tuple(Str("a"), Int(1))) is true
    assert items.includes(Tuple(Str("a"), Int(99))) is false
    assert Tuple(Str("a"), Int(1)) in items
    assert Tuple(Str("missing"), Int(0)) not in items


def test_reversed() -> None:
    items = DictItems(_make())
    rev = items.reversed()
    assert isinstance(rev, DictReverseItemIterator)
    assert rev.next() == Tuple(Str("b"), Int(2))
    assert rev.next() == Tuple(Str("a"), Int(1))


def test_isdisjoint() -> None:
    items = DictItems(_make())
    assert items.isdisjoint(Set(Tuple(Str("x"), Int(0)))) is true
    assert items.isdisjoint(Set(Tuple(Str("a"), Int(1)))) is false


def test_mapping() -> None:
    items = DictItems(_make())
    mp = items.mapping()
    assert isinstance(mp, MappingProxy)


def test_list_escape() -> None:
    items = DictItems(_make())
    lst = items.list()
    assert isinstance(lst, List)
    assert lst == List(Tuple(Str("a"), Int(1)), Tuple(Str("b"), Int(2)))


def test_or_returns_set() -> None:
    items = DictItems(_make())
    other = Set(Tuple(Str("c"), Int(3)))
    result = items | other
    assert isinstance(result, Set)
    expected = {
        Tuple(Str("a"), Int(1)),
        Tuple(Str("b"), Int(2)),
        Tuple(Str("c"), Int(3)),
    }
    assert {x for x in result._data} == expected


def test_and_returns_set() -> None:
    items = DictItems(_make())
    result = items & Set(Tuple(Str("a"), Int(1)), Tuple(Str("x"), Int(0)))
    assert result._data == {Tuple(Str("a"), Int(1))}


def test_sub_returns_set() -> None:
    items = DictItems(_make())
    result = items - Set(Tuple(Str("a"), Int(1)))
    assert result._data == {Tuple(Str("b"), Int(2))}


def test_xor_returns_set() -> None:
    items = DictItems(_make())
    result = items ^ Set(Tuple(Str("b"), Int(2)), Tuple(Str("c"), Int(3)))
    assert result._data == {Tuple(Str("a"), Int(1)), Tuple(Str("c"), Int(3))}


def test_eq_with_dict_items() -> None:
    a = DictItems(_make())
    b = DictItems(_make())
    assert (a == b) is true


def test_eq_with_set() -> None:
    items = DictItems(_make())
    assert (items == Set(Tuple(Str("a"), Int(1)), Tuple(Str("b"), Int(2)))) is true


def test_eq_with_frozen_set() -> None:
    items = DictItems(_make())
    expected = FrozenSet(Tuple(Str("a"), Int(1)), Tuple(Str("b"), Int(2)))
    assert (items == expected) is true


def test_le_lt_ge_gt() -> None:
    items = DictItems(_make())  # {(a,1), (b,2)}
    super_set = Set(
        Tuple(Str("a"), Int(1)),
        Tuple(Str("b"), Int(2)),
        Tuple(Str("c"), Int(3)),
    )
    assert (items <= super_set) is true
    assert (items < super_set) is true
    assert (items >= Set(Tuple(Str("a"), Int(1)))) is true
    assert (items > Set(Tuple(Str("a"), Int(1)))) is true


def test_liveness() -> None:
    d = _make()
    items = DictItems(d)
    assert items.len() == Int(2)
    d.at_put(Str("c"), Int(3))
    assert items.len() == Int(3)


def test_iterable_mixin_do() -> None:
    items = DictItems(_make())
    seen: list[Tuple] = []
    items.do(lambda t: seen.append(t))
    assert seen == [Tuple(Str("a"), Int(1)), Tuple(Str("b"), Int(2))]


def test_iterable_mixin_map() -> None:
    items = DictItems(_make())
    keys = items.map(lambda t: t.at(Int(0)))
    assert keys == List(Str("a"), Str("b"))


def test_str_repr() -> None:
    items = DictItems(_make())
    assert str(items) == "dict_items([('a', 1), ('b', 2)])"


def test_unhashable() -> None:
    with pytest.raises(TypeError):
        hash(DictItems(_make()))
