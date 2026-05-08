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
    from poop.transformers.list import _poop_list_from

    items = DictItems(_make())
    lst = _poop_list_from(items)
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
    assert List(*keys) == List(Str("a"), Str("b"))


def test_str_repr() -> None:
    items = DictItems(_make())
    assert str(items) == "dict_items([('a', 1), ('b', 2)])"


def test_unhashable() -> None:
    with pytest.raises(TypeError):
        hash(DictItems(_make()))


def test_reflected_or() -> None:
    items = DictItems(_make())
    result = Set(Tuple(Str("c"), Int(3))) | items
    assert {x for x in result._data} == {
        Tuple(Str("a"), Int(1)),
        Tuple(Str("b"), Int(2)),
        Tuple(Str("c"), Int(3)),
    }


def test_reflected_and() -> None:
    items = DictItems(_make())
    result = Set(Tuple(Str("a"), Int(1)), Tuple(Str("x"), Int(0))) & items
    assert result._data == {Tuple(Str("a"), Int(1))}


def test_reflected_sub() -> None:
    items = DictItems(_make())
    result = Set(Tuple(Str("a"), Int(1)), Tuple(Str("x"), Int(0))) - items
    assert result._data == {Tuple(Str("x"), Int(0))}


def test_reflected_xor() -> None:
    items = DictItems(_make())
    result = Set(Tuple(Str("b"), Int(2)), Tuple(Str("c"), Int(3))) ^ items
    assert result._data == {Tuple(Str("a"), Int(1)), Tuple(Str("c"), Int(3))}


def test_contains_non_tuple() -> None:
    items = DictItems(_make())
    assert Int(0) not in items
    assert Tuple(Str("a")) not in items  # arity != 2


def test_includes_non_pair() -> None:
    items = DictItems(_make())
    assert items.includes(Tuple(Str("a"))) is false


def test_eq_with_other_type() -> None:
    items = DictItems(_make())
    assert (items == Int(0)) is false


def test_ne() -> None:
    a = DictItems(_make())
    b = DictItems(Dict())
    assert (a != b) is true
    assert (a != a) is false


def test_reversed_dunder() -> None:
    items = DictItems(_make())
    rev = list(reversed(items))
    assert rev[0] == Tuple(Str("b"), Int(2))


def test_other_items_set_of_non_tuples() -> None:
    # _other_items handles Sets of non-Tuple elements gracefully (returns empty pairs)
    items = DictItems(_make())
    other = Set(Int(99))  # not a Tuple
    result = items.isdisjoint(other)
    assert result is true
