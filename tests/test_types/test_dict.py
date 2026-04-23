import pytest

from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
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


def test_at_missing_key_returns_none() -> None:
    assert Dict().at(Str("missing")) is none


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


def test_includes_key_true() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    assert d.includes_key(Str("a")) is true


def test_includes_key_false() -> None:
    assert Dict().includes_key(Str("x")) is false


def test_keys_returns_list() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    d.at_put(Str("b"), Int(2))
    assert isinstance(d.keys(), List)
    assert d.keys().includes(Str("a")) is true
    assert d.keys().includes(Str("b")) is true


def test_values_returns_list() -> None:
    d = Dict()
    d.at_put(Str("a"), Int(1))
    d.at_put(Str("b"), Int(2))
    assert isinstance(d.values(), List)
    assert d.values().includes(Int(1)) is true
    assert d.values().includes(Int(2)) is true


def test_do_receives_tuple_pairs() -> None:
    d = Dict()
    d.at_put(Str("x"), Int(10))
    d.at_put(Str("y"), Int(20))
    pairs: list[Tuple] = []
    d.do(lambda pair: pairs.append(pair))  # type: ignore[arg-type]
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
    assert str(d) == "{a: 1}"


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
    from poop.parser import parse
    from poop.transformers.dict import DictTransformer, _poop_dict_from_pairs
    from poop.transformers.int import IntTransformer
    from poop.transformers.string import StrTransformer
    from poop.types.int import Int as _Int
    from poop.types.string import Str as _Str

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
    from poop.parser import parse
    from poop.transformers.dict import DictTransformer, _poop_dict_from_pairs

    tree = parse("d = {}")
    tree = DictTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_dict_from_pairs": _poop_dict_from_pairs}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert isinstance(ns["d"], Dict)
