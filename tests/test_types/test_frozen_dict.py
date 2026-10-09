"""`FrozenDict` — Python 3.15's `frozendict`, held to CPython's answers.

Every expectation here was checked against `python3.15` first; the comments
quote what it answered.
"""

import pytest

from poop import Interpreter
from poop.errors import ExecutionError
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.dict_items import DictItems
from poop.types.dict_keys import DictKeys
from poop.types.dict_values import DictValues
from poop.types.frozen_dict import FrozenDict
from poop.types.int import Int
from poop.types.list import List
from poop.types.mapping_proxy import MappingProxy
from poop.types.none import none
from poop.types.object import MessageNotUnderstood
from poop.types.string import Str


def _frozen(**pairs: int) -> FrozenDict:
    return FrozenDict._wrapping({Str(k): Int(v) for k, v in pairs.items()})


def _dict(**pairs: int) -> Dict:
    return Dict._wrapping({Str(k): Int(v) for k, v in pairs.items()})


def test_empty() -> None:
    assert FrozenDict().len() == Int(0)
    assert len(FrozenDict()) == 0


def test_class_name_answers_frozendict() -> None:
    assert _frozen(a=1).class_name() == Str("frozendict")


def test_is_not_a_dict() -> None:
    # `isinstance(frozendict(), dict)` is False: it inherits from `object`.
    assert not isinstance(_frozen(a=1), Dict)
    assert _frozen(a=1).is_instance(Dict) is false


def test_the_read_side_is_the_dicts() -> None:
    fd = _frozen(a=1, b=2)
    assert fd.at(Str("a")) == Int(1)
    assert fd.get(Str("z"), Int(5)) == Int(5)
    assert fd.get(Str("z")) is none
    assert fd.includes(Str("a")) is true
    assert fd.len() == Int(2)
    assert isinstance(fd.keys(), DictKeys)
    assert isinstance(fd.values(), DictValues)
    assert isinstance(fd.items(), DictItems)
    assert fd.iter().next() == Str("a")
    assert fd.reversed().next() == Str("b")
    assert fd.min() == Str("a")


def test_at_missing_key_raises() -> None:
    with pytest.raises(KeyError):
        _frozen(a=1).at(Str("z"))


def test_the_views_mapping_is_a_proxy_over_the_frozen_dict() -> None:
    # `frozendict(a=1).keys().mapping` is `mappingproxy(frozendict({'a': 1}))`.
    proxy = _frozen(a=1).keys().mapping()
    assert isinstance(proxy, MappingProxy)
    assert str(proxy) == "mappingproxy(frozendict({'a': 1}))"
    assert proxy.copy() is proxy._dict


def test_copy_answers_the_receiver() -> None:
    # `fd.copy() is fd` is True, as `frozenset.copy` answers itself.
    fd = _frozen(a=1)
    assert fd.copy() is fd


def test_fromkeys() -> None:
    fd = FrozenDict.fromkeys(List(Int(1), Int(2)))
    assert isinstance(fd, FrozenDict)
    assert str(fd) == "frozendict({1: None, 2: None})"
    assert str(FrozenDict.fromkeys(List(Int(1)), Int(0))) == "frozendict({1: 0})"


def test_equality_ignores_order_and_crosses_the_kinds() -> None:
    # `frozendict(a=1, b=2) == frozendict(b=2, a=1)` is True, and so is
    # `frozendict(a=1) == {'a': 1}` in both directions.
    assert _frozen(a=1, b=2) == _frozen(b=2, a=1)
    assert _frozen(a=1) == _dict(a=1)
    assert _dict(a=1) == _frozen(a=1)
    assert _frozen(a=1) == MappingProxy(_dict(a=1))
    assert MappingProxy(_dict(a=1)) == _frozen(a=1)
    assert (_frozen(a=1) == _frozen(a=2)) is false
    assert (_frozen(a=1) == Int(1)) is false


def test_hash_is_by_value_and_order_blind() -> None:
    assert _frozen(a=1, b=2).hash() == _frozen(b=2, a=1).hash()
    assert FrozenDict().hash() == FrozenDict().hash()
    assert _frozen(a=1).hash() != _frozen(a=2).hash()


def test_hashes_so_it_keys_a_dict_and_joins_a_set() -> None:
    d = Dict()
    d.at_put(_frozen(a=1), Str("x"))
    assert d.at(_frozen(a=1)) == Str("x")


def test_an_unhashable_value_refuses_the_hash_in_poops_words() -> None:
    # `hash(frozendict(a=[1]))` is `unhashable type: 'list'`, the bare
    # sentence `Object.hash` rewords; CPython's set-element sentence about a
    # `(key, value)` tuple the program never wrote must not appear.
    fd = FrozenDict._wrapping({Str("a"): List(Int(1))})
    with pytest.raises(TypeError, match="list cannot be hashed") as info:
        fd.hash()
    assert "tuple" not in str(info.value)


def test_or_answers_a_frozen_dict_from_any_mapping() -> None:
    # `fd | {'c': 3}` is a frozendict; `fd | fd` too.
    merged = _frozen(a=1) | _dict(b=2)
    assert isinstance(merged, FrozenDict)
    assert merged == _frozen(a=1, b=2)
    assert isinstance(_frozen(a=1) | _frozen(a=9), FrozenDict)
    assert (_frozen(a=1) | _frozen(a=9)).at(Str("a")) == Int(9)
    assert isinstance(_frozen(a=1) | MappingProxy(_dict(b=2)), FrozenDict)


def test_dict_or_frozen_dict_answers_a_dict() -> None:
    # `{'c': 3} | fd` is a dict: the left operand's kind, as the set pair.
    merged = _dict(c=3) | _frozen(a=1)
    assert isinstance(merged, Dict)
    assert str(merged) == "{'c': 3, 'a': 1}"


def test_or_with_a_non_mapping_is_a_refused_message() -> None:
    with pytest.raises(
        ExecutionError, match="frozendict does not understand #\\| with an int"
    ):
        Interpreter().run_source("frozendict(a=1) | 5")


def test_a_dict_updates_from_a_frozen_dict() -> None:
    d = _dict(x=0)
    assert d.update(_frozen(a=1)) is none
    d |= _frozen(b=2)
    assert str(d) == "{'x': 0, 'a': 1, 'b': 2}"


def test_the_writes_are_refused_with_the_dict_hint() -> None:
    # `fd.update({})` is `AttributeError: ... Did you mean to use a 'dict'
    # object?` in CPython; `at_put` is POOP's `d[k] = v`, so it says the same.
    for name in ("update", "at_put", "pop", "popitem", "setdefault", "clear"):
        with pytest.raises(MessageNotUnderstood, match=f"does not understand #{name}"):
            getattr(_frozen(a=1), name)
    with pytest.raises(MessageNotUnderstood, match="did you mean to use a dict\\?"):
        _frozen(a=1).update  # noqa: B018  # ty: ignore[unresolved-attribute]
    with pytest.raises(MessageNotUnderstood, match="did you mean to use a dict\\?"):
        _frozen(a=1).at_put  # noqa: B018  # ty: ignore[unresolved-attribute]


def test_str_and_repr() -> None:
    assert str(FrozenDict()) == "frozendict()"
    assert repr(_frozen(a=1, b=2)) == "frozendict({'a': 1, 'b': 2})"


def test_a_cycle_through_a_dict_prints_the_ellipsis() -> None:
    d = Dict()
    fd = FrozenDict._wrapping({Str("d"): d})
    d.at_put(Str("fd"), fd)
    assert str(fd) == "frozendict({'d': {'fd': frozendict({...})}})"


def test_the_collection_messages_walk_the_keys() -> None:
    fd = _frozen(a=1, b=2)
    assert List(*fd.map(lambda k: k.upper())) == List(Str("A"), Str("B"))
    assert fd.all(lambda k: k.len() == Int(1)) is true
    seen: list[object] = []
    fd.do(seen.append)
    assert seen == [Str("a"), Str("b")]
