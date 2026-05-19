import pytest

from poop.parser import parse
from poop.transformers.dict import DictTransformer, _poop_dict_from_pairs
from poop.transformers.int import IntTransformer
from poop.transformers.string import StrTransformer
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.dict_items import DictItems
from poop.types.dict_keys import DictKeys
from poop.types.dict_values import DictValues
from poop.types.int import Int
from poop.types.int import Int as _Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.string import Str as _Str
from poop.types.tuple import Tuple


def test_empty_dict() -> None:
    assert Dict().len() == Int(0)


def test_len() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    d.at_put(Str("b"), Int(2))
    assert d.len() == Int(2)


def test_dunder_len() -> None:
    d = Dict()
    d.at_put(Str("x"), Int(0))
    assert len(d) == 1


def test_at_existing_key() -> None:
    d = Dict()
    d.at_put(Str("k"), Int(42))
    assert d.at(Str("k")) == Int(42)


def test_at_missing_key_raises() -> None:
    with pytest.raises(KeyError):
        Dict().at(Str("missing"))


def test_get_existing_key() -> None:
    d = Dict()
    d.at_put(Str("k"), Int(42))
    assert d.get(Str("k")) == Int(42)


def test_get_missing_key_returns_none() -> None:
    assert Dict().get(Str("missing")) is none


def test_get_missing_key_with_default() -> None:
    assert Dict().get(Str("missing"), Int(99)) == Int(99)


def test_get_existing_key_ignores_default() -> None:
    d = Dict()
    d.at_put(Str("k"), Int(1))
    assert d.get(Str("k"), Int(99)) == Int(1)


def test_at_put_returns_self() -> None:
    d = Dict()
    result = d.at_put(Str("k"), Int(1))
    assert result is d


def test_at_put_updates_existing() -> None:
    d = Dict()
    d.at_put(Str("k"), Int(1))
    d.at_put(Str("k"), Int(99))
    assert d.at(Str("k")) == Int(99)
    assert d.len() == Int(1)


def test_includes_true() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    assert d.includes(Str("a")) is true


def test_includes_false() -> None:
    assert Dict().includes(Str("x")) is false


def test_keys_returns_dict_keys_view() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    d.at_put(Str("b"), Int(2))
    assert isinstance(d.keys(), DictKeys)
    assert d.keys().includes(Str("a")) is true
    assert d.keys().includes(Str("b")) is true


def test_values_returns_dict_values_view() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    d.at_put(Str("b"), Int(2))
    assert isinstance(d.values(), DictValues)
    assert d.values().includes(Int(1)) is true
    assert d.values().includes(Int(2)) is true


def test_do_receives_tuple_pairs() -> None:
    d = Dict()
    d.at_put(Str("x"), Int(10))
    d.at_put(Str("y"), Int(20))
    pairs: list[Tuple] = []
    d.do(lambda pair: pairs.append(pair))
    assert len(pairs) == 2
    assert all(isinstance(p, Tuple) for p in pairs)


def test_eq_equal_dicts() -> None:
    d1, d2 = Dict(), Dict()
    d1.at_put(Str("k"), Int(1))
    d2.at_put(Str("k"), Int(1))
    assert d1 == d2


def test_eq_different_dicts() -> None:
    d1, d2 = Dict(), Dict()
    d1.at_put(Str("k"), Int(1))
    d2.at_put(Str("k"), Int(2))
    assert (d1 == d2) is false


def test_ne_different_dicts() -> None:
    d1, d2 = Dict(), Dict()
    d1.at_put(Str("k"), Int(1))
    assert (d1 != d2) is true


def test_str_empty() -> None:
    assert str(Dict()) == "{}"


def test_str_representation() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    assert str(d) == "{'a': 1}"


def test_repr_equals_str() -> None:
    d = Dict()
    d.at_put(Str("k"), Int(0))
    assert repr(d) == str(d)


def test_not_hashable() -> None:
    with pytest.raises(TypeError):
        hash(Dict())


def test_contains_dunder() -> None:
    d = Dict()
    d.at_put(Str("k"), Int(1))
    assert Str("k") in d
    assert Str("z") not in d


def test_iter_yields_keys() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    d.at_put(Str("b"), Int(2))
    keys = list(d)
    assert Str("a") in keys
    assert Str("b") in keys


def test_transformer_literal() -> None:
    tree = parse('d = {"hello": 1}')
    tree = StrTransformer().transform(tree)
    tree = IntTransformer().transform(tree)
    tree = DictTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_dict_from_pairs": _poop_dict_from_pairs,
        "_poop_int": _Int,
        "_poop_str": _Str,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["d"], Dict)


def test_transformer_empty_literal() -> None:
    tree = parse("d = {}")
    tree = DictTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_dict_from_pairs": _poop_dict_from_pairs}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["d"], Dict)


def _dict_with(pairs: list[tuple[object, object]]) -> Dict:
    d = Dict()
    for k, v in pairs:
        key = Int(k) if isinstance(k, int) else Str(str(k))
        val = Int(v) if isinstance(v, int) else Str(str(v))
        d.at_put(key, val)
    return d


def test_clear_empties_dict() -> None:
    d = _dict_with([(1, 10), (2, 20)])
    d.clear()
    assert d.len() == Int(0)


def test_clear_returns_none() -> None:
    d = _dict_with([(1, 10)])
    assert d.clear() is none


def test_copy_returns_new_dict() -> None:
    d = _dict_with([(1, 10)])
    c = d.copy()
    assert c is not d
    assert c == d


def test_copy_is_shallow() -> None:
    d = _dict_with([(1, 10)])
    c = d.copy()
    d.clear()
    assert c.len() == Int(1)


def test_items_returns_dict_items_view() -> None:
    from poop.transformers.list import _poop_list_from

    d = Dict()
    d.at_put(Int(1), Int(10))
    items = d.items()
    assert isinstance(items, DictItems)
    assert _poop_list_from(items) == List(Tuple(Int(1), Int(10)))


def test_pop_removes_and_returns_value() -> None:
    d = _dict_with([(1, 10), (2, 20)])
    val = d.pop(Int(1))
    assert val == Int(10)
    assert d.len() == Int(1)


def test_pop_missing_key_raises_keyerror() -> None:
    # Matches Python: dict.pop(key) without default raises KeyError.
    d = _dict_with([(1, 10)])
    with pytest.raises(KeyError):
        d.pop(Int(99))


def test_pop_missing_key_with_explicit_default_returns_default() -> None:
    d = _dict_with([(1, 10)])
    assert d.pop(Int(99), none) is none
    assert d.pop(Int(99), Int(-1)) == Int(-1)


def test_popitem_returns_last_pair() -> None:
    d = Dict()
    d.at_put(Int(1), Int(10))
    d.at_put(Int(2), Int(20))
    result = d.popitem()
    assert result == Tuple(Int(2), Int(20))
    assert d.len() == Int(1)


def test_setdefault_existing_key() -> None:
    d = _dict_with([(1, 10)])
    val = d.setdefault(Int(1), Int(99))
    assert val == Int(10)


def test_setdefault_missing_key_inserts() -> None:
    d = _dict_with([(1, 10)])
    val = d.setdefault(Int(2), Int(99))
    assert val == Int(99)
    assert d.at(Int(2)) == Int(99)


def test_update_merges_dicts() -> None:
    d1 = _dict_with([(1, 10)])
    d2 = _dict_with([(2, 20)])
    d1.update(d2)
    assert d1.len() == Int(2)
    assert d1.at(Int(2)) == Int(20)


def test_update_returns_none() -> None:
    d1 = _dict_with([(1, 10)])
    d2 = _dict_with([(2, 20)])
    assert d1.update(d2) is none


def test_eq_with_non_dict_returns_false() -> None:
    assert Dict().__eq__(Int(1)) is false


def test_ne_with_non_dict_returns_true() -> None:
    assert Dict().__ne__(Int(1)) is true


def test_fromkeys_with_default_none() -> None:
    result = Dict.fromkeys(List(Str("a"), Str("b"), Str("c")))
    assert result.at(Str("a")) is none
    assert result.at(Str("b")) is none
    assert result.at(Str("c")) is none
    assert result.len() == Int(3)


def test_fromkeys_with_explicit_value() -> None:
    result = Dict.fromkeys(List(Str("x"), Str("y")), Int(0))
    assert result.at(Str("x")) == Int(0)
    assert result.at(Str("y")) == Int(0)


def test_fromkeys_empty_keys() -> None:
    result = Dict.fromkeys(List())
    assert result.len() == Int(0)


# --- New: explicit default for pop (proposal 32, v1.2.0) ---


def test_pop_with_explicit_default() -> None:
    d = Dict()
    d.at_put(Int(1), Int(10))
    assert d.pop(Int(99), Str("missing")) == Str("missing")
    assert d.pop(Int(1), Str("missing")) == Int(10)
