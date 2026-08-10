from poop.parser import parse
from poop.transformers.frozen_set import FrozenSetTransformer, _poop_frozenset_from
from poop.transformers.int import IntTransformer
from poop.transformers.set import SetTransformer, _poop_set
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.int import Int as _Int
from poop.types.none import none
from poop.types.set import Set
from poop.types.string import Str


def test_empty_frozenset() -> None:
    assert FrozenSet().len() == Int(0)


def test_len() -> None:
    assert FrozenSet(Int(1), Int(2), Int(3)).len() == Int(3)


def test_dunder_len() -> None:
    assert len(FrozenSet(Int(1), Int(2))) == 2


def test_duplicate_elements_kept_unique() -> None:
    assert FrozenSet(Int(1), Int(1)).len() == Int(1)


def test_includes_true() -> None:
    assert FrozenSet(Int(1), Int(2)).includes(Int(1)) is true


def test_includes_false() -> None:
    assert FrozenSet().includes(Int(1)) is false


def test_contains_dunder() -> None:
    fs = FrozenSet(Int(1), Int(2))
    assert Int(1) in fs
    assert Int(99) not in fs


def test_do_visits_all_elements() -> None:
    fs = FrozenSet(Int(1), Int(2), Int(3))
    seen: list[Int] = []
    fs.do(lambda x: seen.append(x))
    assert len(seen) == 3


def test_map_returns_lazy_map() -> None:
    from poop.types.map import Map

    result = FrozenSet(Int(1), Int(2)).map(lambda x: x)
    assert isinstance(result, Map)


def test_map_transforms_elements() -> None:
    result = FrozenSet(*FrozenSet(Int(2)).map(lambda x: Int(x._value * 3)))
    assert result.includes(Int(6)) is true


def test_filter_keeps_matching() -> None:
    fs = FrozenSet(Int(1), Int(2), Int(3), Int(4))
    result = FrozenSet(*fs.filter(lambda x: x._value % 2 == 0))
    assert result.len() == Int(2)
    assert result.includes(Int(2)) is true
    assert result.includes(Int(4)) is true


def test_filter_false_keeps_non_matching() -> None:
    fs = FrozenSet(Int(1), Int(2), Int(3))
    result = FrozenSet(*fs.filter_false(lambda x: x._value % 2 == 0))
    assert result.len() == Int(2)


def test_find_returns_matching_element() -> None:
    fs = FrozenSet(Int(5))
    result = fs.find(lambda x: x._value > 3)
    assert result == Int(5)


def test_find_returns_none_when_not_found() -> None:
    assert FrozenSet(Int(1)).find(lambda x: x._value > 99) is none


def test_sum_returns_total() -> None:
    assert FrozenSet(Int(1), Int(2), Int(3)).sum() == Int(6)


def test_sum_empty_returns_zero() -> None:
    assert FrozenSet().sum() == Int(0)


def test_all_true_when_all_match() -> None:
    assert FrozenSet(Int(2), Int(4)).all(lambda x: x._value % 2 == 0) is true


def test_all_false_when_any_mismatch() -> None:
    assert FrozenSet(Int(2), Int(3)).all(lambda x: x._value % 2 == 0) is false


def test_any_true_when_some_match() -> None:
    assert FrozenSet(Int(1), Int(2)).any(lambda x: x._value % 2 == 0) is true


def test_any_false_when_none_match() -> None:
    assert FrozenSet(Int(1), Int(3)).any(lambda x: x._value % 2 == 0) is false


def test_eq_equal_frozensets() -> None:
    assert FrozenSet(Int(1), Int(2)) == FrozenSet(Int(2), Int(1))


def test_eq_different_frozensets() -> None:
    assert (FrozenSet(Int(1)) == FrozenSet(Int(2))) is false


def test_ne_different_frozensets() -> None:
    assert (FrozenSet(Int(1)) != FrozenSet(Int(2))) is true


def test_iter_yields_all_elements() -> None:
    assert len(list(FrozenSet(Int(1), Int(2), Int(3)))) == 3


def test_hashable() -> None:
    fs = FrozenSet(Int(1), Int(2))
    assert isinstance(hash(fs), int)


def test_equal_frozensets_have_equal_hash() -> None:
    fs1 = FrozenSet(Int(1), Int(2))
    fs2 = FrozenSet(Int(2), Int(1))
    assert hash(fs1) == hash(fs2)


def test_frozenset_can_be_dict_key() -> None:
    d = Dict()
    fs = FrozenSet(Int(1))
    d.at_put(fs, Str("value"))
    assert d.at(fs) == Str("value")


def test_str_empty() -> None:
    assert str(FrozenSet()) == "frozenset()"


def test_str_contains_elements() -> None:
    assert "1" in str(FrozenSet(Int(1)))


def test_repr_equals_str() -> None:
    fs = FrozenSet(Int(1))
    assert repr(fs) == str(fs)


def test_transformer_frozenset_call() -> None:
    tree = parse("fs = frozenset({1, 2, 3})")
    tree = IntTransformer().transform(tree)
    tree = SetTransformer().transform(tree)
    tree = FrozenSetTransformer().transform(tree)
    ns: dict[str, object] = {
        "_poop_frozenset_from": _poop_frozenset_from,
        "_poop_set": _poop_set,
        "_poop_int": _Int,
    }
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["fs"]
    assert isinstance(result, FrozenSet)
    assert result.len() == Int(3)


def test_transformer_frozenset_empty_call() -> None:
    tree = parse("fs = frozenset()")
    tree = FrozenSetTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_frozenset_from": _poop_frozenset_from}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["fs"]
    assert isinstance(result, FrozenSet)
    assert result.len() == Int(0)


def test_copy_returns_self() -> None:
    # CPython returns the receiver itself: a frozenset is immutable, so
    # ``fs.copy() is fs`` is True.
    fs = FrozenSet(Int(1), Int(2))
    c = fs.copy()
    assert c is fs
    assert c == fs


def test_union() -> None:
    assert FrozenSet(Int(1), Int(2)).union(FrozenSet(Int(2), Int(3))) == FrozenSet(
        Int(1), Int(2), Int(3)
    )


def test_union_multiple_others() -> None:
    assert FrozenSet(Int(1)).union(FrozenSet(Int(2)), FrozenSet(Int(3))) == FrozenSet(
        Int(1), Int(2), Int(3)
    )


def test_union_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    assert FrozenSet(Int(1), Int(2)).union(List(Int(3))) == FrozenSet(
        Int(1), Int(2), Int(3)
    )


def test_difference_accepts_non_set_iterable() -> None:
    from poop.types.tuple import Tuple

    assert FrozenSet(Int(1), Int(2), Int(3)).difference(Tuple(Int(2))) == FrozenSet(
        Int(1), Int(3)
    )


def test_symmetric_difference_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    assert FrozenSet(Int(1), Int(2)).symmetric_difference(
        List(Int(2), Int(3))
    ) == FrozenSet(Int(1), Int(3))


def test_isdisjoint_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    assert FrozenSet(Int(1)).isdisjoint(List(Int(2))) is true


def test_issubset_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    assert FrozenSet(Int(1), Int(2)).issubset(List(Int(1), Int(2), Int(3))) is true


def test_issuperset_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    assert FrozenSet(Int(1), Int(2), Int(3)).issuperset(List(Int(1))) is true


def test_intersection() -> None:
    assert FrozenSet(Int(1), Int(2), Int(3)).intersection(
        FrozenSet(Int(2), Int(3), Int(4))
    ) == FrozenSet(Int(2), Int(3))


def test_difference() -> None:
    assert FrozenSet(Int(1), Int(2), Int(3)).difference(
        FrozenSet(Int(2), Int(3))
    ) == FrozenSet(Int(1))


def test_symmetric_difference() -> None:
    result = FrozenSet(Int(1), Int(2), Int(3)).symmetric_difference(
        FrozenSet(Int(2), Int(3), Int(4))
    )
    assert result == FrozenSet(Int(1), Int(4))


def test_isdisjoint_true() -> None:
    assert FrozenSet(Int(1), Int(2)).isdisjoint(FrozenSet(Int(3), Int(4))) is true


def test_isdisjoint_false() -> None:
    assert FrozenSet(Int(1), Int(2)).isdisjoint(FrozenSet(Int(2), Int(3))) is false


def test_issubset_true() -> None:
    assert FrozenSet(Int(1), Int(2)).issubset(FrozenSet(Int(1), Int(2), Int(3))) is true


def test_issubset_false() -> None:
    assert (
        FrozenSet(Int(1), Int(4)).issubset(FrozenSet(Int(1), Int(2), Int(3))) is false
    )


def test_issuperset_true() -> None:
    assert (
        FrozenSet(Int(1), Int(2), Int(3)).issuperset(FrozenSet(Int(1), Int(2))) is true
    )


def test_issuperset_false() -> None:
    assert FrozenSet(Int(1), Int(2)).issuperset(FrozenSet(Int(1), Int(3))) is false


def test_eq_with_non_frozenset_returns_false() -> None:
    assert FrozenSet(Int(1)).__eq__(Int(1)) is false


def test_ne_with_non_frozenset_returns_true() -> None:
    assert FrozenSet(Int(1)).__ne__(Int(1)) is true


def test_dunder_and_intersection() -> None:
    a = FrozenSet(Int(1), Int(2), Int(3))
    b = FrozenSet(Int(2), Int(3), Int(4))
    assert a & b == FrozenSet(Int(2), Int(3))


def test_dunder_or_union() -> None:
    a = FrozenSet(Int(1), Int(2))
    b = FrozenSet(Int(2), Int(3))
    assert a | b == FrozenSet(Int(1), Int(2), Int(3))


def test_dunder_sub_difference() -> None:
    a = FrozenSet(Int(1), Int(2), Int(3))
    b = FrozenSet(Int(2))
    assert a - b == FrozenSet(Int(1), Int(3))


def test_dunder_xor_symmetric_difference() -> None:
    a = FrozenSet(Int(1), Int(2))
    b = FrozenSet(Int(2), Int(3))
    assert a ^ b == FrozenSet(Int(1), Int(3))


def test_dunder_ops_return_notimplemented_on_wrong_type() -> None:
    # Matches Set's defensive pattern: operators against non-FrozenSet
    # return NotImplemented so Python falls through to TypeError.
    f = FrozenSet(Int(1))
    import pytest as _pytest

    with _pytest.raises(TypeError):
        _ = f & "wrong"
    with _pytest.raises(TypeError):
        _ = f | "wrong"
    with _pytest.raises(TypeError):
        _ = f - "wrong"
    with _pytest.raises(TypeError):
        _ = f ^ "wrong"


def test_eq_set_and_frozenset_equal_by_value() -> None:
    # CPython: {1, 2} == frozenset({1, 2}) is True (both directions).
    assert FrozenSet(Int(1), Int(2)) == Set(Int(1), Int(2))
    assert Set(Int(1), Int(2)) == FrozenSet(Int(1), Int(2))


def test_eq_set_and_frozenset_different_values() -> None:
    assert (FrozenSet(Int(1), Int(2)) == Set(Int(1), Int(3))) is false
    assert (FrozenSet(Int(1), Int(2)) != Set(Int(1), Int(3))) is true


def test_lt_proper_subset_true() -> None:
    assert (FrozenSet(Int(1), Int(2)) < FrozenSet(Int(1), Int(2), Int(3))) is true


def test_le_subset_true() -> None:
    assert (FrozenSet(Int(1), Int(2)) <= FrozenSet(Int(1), Int(2))) is true


def test_gt_proper_superset_true() -> None:
    assert (FrozenSet(Int(1), Int(2), Int(3)) > FrozenSet(Int(1), Int(2))) is true


def test_comparison_mixes_with_set() -> None:
    assert (FrozenSet(Int(1), Int(2), Int(3)) > Set(Int(1), Int(2))) is true


def test_a_set_argument_can_be_asked_about() -> None:
    # The reading half of `Set`'s fix: `fs.includes({1})` is a question, and
    # a `set` is unhashable only for *storing*.
    from poop.types.set import Set

    assert FrozenSet(Int(1)).includes(Set(Int(1))) is false
    assert FrozenSet(FrozenSet(Int(1))).includes(Set(Int(1))) is true
