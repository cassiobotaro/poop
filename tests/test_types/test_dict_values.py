import pytest

from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.dict_reverse_value_iterator import DictReverseValueIterator
from poop.types.dict_value_iterator import DictValueIterator
from poop.types.dict_values import DictValues
from poop.types.int import Int
from poop.types.list import List
from poop.types.mapping_proxy import MappingProxy
from poop.types.string import Str


def _make() -> Dict:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    d.at_put(Str("b"), Int(2))
    return d


def test_iter_returns_dict_value_iterator() -> None:
    values = DictValues(_make())
    assert isinstance(values.iter(), DictValueIterator)


def test_iter_yields_values() -> None:
    values = DictValues(_make())
    it = values.iter()
    assert it.next() == Int(1)
    assert it.next() == Int(2)


def test_len() -> None:
    values = DictValues(_make())
    assert values.len() == Int(2)
    assert len(values) == 2


def test_contains_via_iteration() -> None:
    values = DictValues(_make())
    assert values.includes(Int(1)) is true
    assert values.includes(Int(99)) is false
    assert Int(1) in values
    assert Int(99) not in values


def test_reversed() -> None:
    values = DictValues(_make())
    rev = values.reversed()
    assert isinstance(rev, DictReverseValueIterator)
    assert rev.next() == Int(2)
    assert rev.next() == Int(1)


def test_mapping() -> None:
    values = DictValues(_make())
    mp = values.mapping()
    assert isinstance(mp, MappingProxy)


def test_list_escape() -> None:
    from poop.transformers.list import _poop_list_from

    values = DictValues(_make())
    lst = _poop_list_from(values)
    assert isinstance(lst, List)
    assert lst == List(Int(1), Int(2))


def test_no_set_ops() -> None:
    a = DictValues(_make())
    # Set operators are not implemented (Python parity — values may be unhashable).
    assert not hasattr(a, "__or__")
    assert not hasattr(a, "__and__")
    assert not hasattr(a, "__sub__")
    assert not hasattr(a, "__xor__")
    assert not hasattr(a, "isdisjoint")


def test_eq_inherits_identity() -> None:
    # Python's dict_values does not implement useful equality. POOP inherits
    # Object's identity-based __eq__ — same effect.
    a = DictValues(_make())
    b = DictValues(_make())
    assert (a == b) is false
    assert (a == a) is true


def test_liveness() -> None:
    d = _make()
    values = DictValues(d)
    assert values.len() == Int(2)
    d.at_put(Str("c"), Int(3))
    assert values.len() == Int(3)
    assert values.includes(Int(3)) is true


def test_iterable_mixin_do() -> None:
    values = DictValues(_make())
    seen: list[Int] = []
    values.do(lambda v: seen.append(v))
    assert seen == [Int(1), Int(2)]


def test_str_repr() -> None:
    values = DictValues(_make())
    assert str(values) == "dict_values([1, 2])"


def test_unhashable() -> None:
    with pytest.raises(TypeError):
        hash(DictValues(_make()))


def test_reversed_dunder() -> None:
    values = DictValues(_make())
    assert list(reversed(values)) == [Int(2), Int(1)]
