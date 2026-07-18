import pytest

from poop.parser import parse
from poop.transformers.int import IntTransformer
from poop.transformers.set import SetTransformer, _poop_set
from poop.types.boolean import false, true
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.int import Int as _Int
from poop.types.none import none
from poop.types.set import Set


def test_empty_set() -> None:
    assert Set().len() == Int(0)


def test_len() -> None:
    s = Set(Int(1), Int(2), Int(3))
    assert s.len() == Int(3)


def test_dunder_len() -> None:
    assert len(Set(Int(1), Int(2))) == 2


def test_add_returns_none() -> None:
    s = Set()
    result = s.add(Int(1))
    assert result is none


def test_add_increases_len() -> None:
    s = Set()
    s.add(Int(1))
    s.add(Int(2))
    assert s.len() == Int(2)


def test_add_duplicate_keeps_unique() -> None:
    s = Set(Int(1))
    s.add(Int(1))
    assert s.len() == Int(1)


def test_remove_returns_none() -> None:
    s = Set(Int(1))
    result = s.remove(Int(1))
    assert result is none


def test_remove_decreases_len() -> None:
    s = Set(Int(1), Int(2))
    s.remove(Int(1))
    assert s.len() == Int(1)


def test_remove_missing_raises() -> None:
    s = Set()
    with pytest.raises(KeyError):
        s.remove(Int(99))


def test_includes_true() -> None:
    s = Set(Int(1), Int(2))
    assert s.includes(Int(1)) is true


def test_includes_false() -> None:
    assert Set().includes(Int(1)) is false


def test_contains_dunder() -> None:
    s = Set(Int(1), Int(2))
    assert Int(1) in s
    assert Int(99) not in s


def test_do_visits_all_elements() -> None:
    s = Set(Int(1), Int(2), Int(3))
    seen: list[Int] = []
    s.do(lambda x: seen.append(x))
    assert len(seen) == 3


def test_map_returns_lazy_map() -> None:
    from poop.types.map import Map

    s = Set(Int(1), Int(2))
    result = s.map(lambda x: x)
    assert isinstance(result, Map)


def test_map_transforms_elements() -> None:
    s = Set(Int(2))
    result = Set(*s.map(lambda x: Int(x._value * 2)))
    assert result.includes(Int(4)) is true


def test_filter_keeps_matching() -> None:
    s = Set(Int(1), Int(2), Int(3), Int(4))
    result = Set(*s.filter(lambda x: x._value % 2 == 0))
    assert result.len() == Int(2)
    assert result.includes(Int(2)) is true
    assert result.includes(Int(4)) is true


def test_filter_false_keeps_non_matching() -> None:
    s = Set(Int(1), Int(2), Int(3))
    result = Set(*s.filter_false(lambda x: x._value % 2 == 0))
    assert result.len() == Int(2)


def test_find_returns_matching_element() -> None:
    s = Set(Int(1), Int(2), Int(3))
    result = s.find(lambda x: x._value > 2)
    assert result == Int(3)


def test_find_returns_none_when_not_found() -> None:
    s = Set(Int(1), Int(2))
    assert s.find(lambda x: x._value > 99) is none


def test_sum_returns_total() -> None:
    assert Set(Int(1), Int(2), Int(3)).sum() == Int(6)


def test_sum_empty_returns_zero() -> None:
    assert Set().sum() == Int(0)


def test_all_true_when_all_match() -> None:
    s = Set(Int(2), Int(4))
    assert s.all(lambda x: x._value % 2 == 0) is true


def test_all_false_when_any_mismatch() -> None:
    s = Set(Int(2), Int(3))
    assert s.all(lambda x: x._value % 2 == 0) is false


def test_any_true_when_some_match() -> None:
    s = Set(Int(1), Int(2))
    assert s.any(lambda x: x._value % 2 == 0) is true


def test_any_false_when_none_match() -> None:
    s = Set(Int(1), Int(3))
    assert s.any(lambda x: x._value % 2 == 0) is false


def test_eq_equal_sets() -> None:
    assert Set(Int(1), Int(2)) == Set(Int(2), Int(1))


def test_eq_different_sets() -> None:
    assert (Set(Int(1)) == Set(Int(2))) is false


def test_ne_different_sets() -> None:
    assert (Set(Int(1)) != Set(Int(2))) is true


def test_iter_yields_all_elements() -> None:
    s = Set(Int(1), Int(2), Int(3))
    items = list(s)
    assert len(items) == 3


def test_str_empty() -> None:
    assert str(Set()) == "set()"


def test_str_contains_elements() -> None:
    s = Set(Int(1))
    assert "1" in str(s)


def test_repr_equals_str() -> None:
    s = Set(Int(1))
    assert repr(s) == str(s)


def test_not_hashable() -> None:
    with pytest.raises(TypeError):
        hash(Set())


def test_transformer_literal() -> None:
    tree = parse("s = {1, 2, 3}")
    tree = IntTransformer().transform(tree)
    tree = SetTransformer().transform(tree)
    ns: dict[str, object] = {"_poop_set": _poop_set, "_poop_int": _Int}
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    result = ns["s"]
    assert isinstance(result, Set)
    assert result.len() == Int(3)


def test_discard_removes_element() -> None:
    s = Set(Int(1), Int(2))
    s.discard(Int(1))
    assert s.len() == Int(1)


def test_discard_missing_does_not_raise() -> None:
    s = Set(Int(1))
    s.discard(Int(99))
    assert s.len() == Int(1)


def test_discard_returns_none() -> None:
    s = Set(Int(1))
    assert s.discard(Int(1)) is none


def test_clear_empties_set() -> None:
    s = Set(Int(1), Int(2))
    s.clear()
    assert s.len() == Int(0)


def test_clear_returns_none() -> None:
    s = Set(Int(1))
    assert s.clear() is none


def test_copy_returns_new_set() -> None:
    s = Set(Int(1), Int(2))
    c = s.copy()
    assert c is not s
    assert c == s


def test_copy_is_shallow() -> None:
    s = Set(Int(1))
    c = s.copy()
    s.clear()
    assert c.len() == Int(1)


def test_pop_removes_an_element() -> None:
    s = Set(Int(1))
    val = s.pop()
    assert val == Int(1)
    assert s.len() == Int(0)


def test_union_returns_combined_set() -> None:
    assert Set(Int(1), Int(2)).union(Set(Int(2), Int(3))) == Set(Int(1), Int(2), Int(3))


def test_union_multiple_others() -> None:
    assert Set(Int(1)).union(Set(Int(2)), Set(Int(3))) == Set(Int(1), Int(2), Int(3))


def test_union_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    assert Set(Int(1), Int(2)).union(List(Int(2), Int(3))) == Set(
        Int(1), Int(2), Int(3)
    )


def test_intersection_accepts_non_set_iterable() -> None:
    from poop.types.tuple import Tuple

    assert Set(Int(1), Int(2), Int(3)).intersection(Tuple(Int(2), Int(3))) == Set(
        Int(2), Int(3)
    )


def test_difference_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    assert Set(Int(1), Int(2), Int(3)).difference(List(Int(2))) == Set(Int(1), Int(3))


def test_symmetric_difference_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    assert Set(Int(1), Int(2)).symmetric_difference(List(Int(2), Int(3))) == Set(
        Int(1), Int(3)
    )


def test_update_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    s = Set(Int(1))
    s.update(List(Int(2), Int(3)))
    assert s == Set(Int(1), Int(2), Int(3))


def test_intersection_update_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    s = Set(Int(1), Int(2), Int(3))
    s.intersection_update(List(Int(2), Int(3)))
    assert s == Set(Int(2), Int(3))


def test_difference_update_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    s = Set(Int(1), Int(2), Int(3))
    s.difference_update(List(Int(1)))
    assert s == Set(Int(2), Int(3))


def test_symmetric_difference_update_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    s = Set(Int(1), Int(2))
    s.symmetric_difference_update(List(Int(2), Int(3)))
    assert s == Set(Int(1), Int(3))


def test_isdisjoint_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    assert Set(Int(1), Int(2)).isdisjoint(List(Int(3))) is true


def test_issubset_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    assert Set(Int(1), Int(2)).issubset(List(Int(1), Int(2), Int(3))) is true


def test_issuperset_accepts_non_set_iterable() -> None:
    from poop.types.list import List

    assert Set(Int(1), Int(2), Int(3)).issuperset(List(Int(1), Int(2))) is true


def test_intersection() -> None:
    assert Set(Int(1), Int(2), Int(3)).intersection(Set(Int(2), Int(3), Int(4))) == Set(
        Int(2), Int(3)
    )


def test_difference() -> None:
    assert Set(Int(1), Int(2), Int(3)).difference(Set(Int(2), Int(3))) == Set(Int(1))


def test_symmetric_difference() -> None:
    assert Set(Int(1), Int(2), Int(3)).symmetric_difference(
        Set(Int(2), Int(3), Int(4))
    ) == Set(Int(1), Int(4))


def test_update_mutates() -> None:
    s = Set(Int(1))
    s.update(Set(Int(2), Int(3)))
    assert s == Set(Int(1), Int(2), Int(3))


def test_update_returns_none() -> None:
    s = Set(Int(1))
    assert s.update(Set(Int(2))) is none


def test_intersection_update() -> None:
    s = Set(Int(1), Int(2), Int(3))
    s.intersection_update(Set(Int(2), Int(3), Int(4)))
    assert s == Set(Int(2), Int(3))


def test_difference_update() -> None:
    s = Set(Int(1), Int(2), Int(3))
    s.difference_update(Set(Int(2), Int(3)))
    assert s == Set(Int(1))


def test_symmetric_difference_update() -> None:
    s = Set(Int(1), Int(2), Int(3))
    s.symmetric_difference_update(Set(Int(2), Int(3), Int(4)))
    assert s == Set(Int(1), Int(4))


def test_isdisjoint_true() -> None:
    assert Set(Int(1), Int(2)).isdisjoint(Set(Int(3), Int(4))) is true


def test_isdisjoint_false() -> None:
    assert Set(Int(1), Int(2)).isdisjoint(Set(Int(2), Int(3))) is false


def test_issubset_true() -> None:
    assert Set(Int(1), Int(2)).issubset(Set(Int(1), Int(2), Int(3))) is true


def test_issubset_false() -> None:
    assert Set(Int(1), Int(4)).issubset(Set(Int(1), Int(2), Int(3))) is false


def test_issuperset_true() -> None:
    assert Set(Int(1), Int(2), Int(3)).issuperset(Set(Int(1), Int(2))) is true


def test_issuperset_false() -> None:
    assert Set(Int(1), Int(2)).issuperset(Set(Int(1), Int(3))) is false


def test_eq_with_non_set_returns_false() -> None:
    assert Set(Int(1)).__eq__(Int(1)) is false


def test_ne_with_non_set_returns_true() -> None:
    assert Set(Int(1)).__ne__(Int(1)) is true


def test_dunder_and_intersection() -> None:
    assert Set(Int(1), Int(2), Int(3)) & Set(Int(2), Int(3), Int(4)) == Set(
        Int(2), Int(3)
    )


def test_dunder_or_union() -> None:
    assert Set(Int(1), Int(2)) | Set(Int(2), Int(3)) == Set(Int(1), Int(2), Int(3))


def test_dunder_sub_difference() -> None:
    assert Set(Int(1), Int(2), Int(3)) - Set(Int(2)) == Set(Int(1), Int(3))


def test_dunder_xor_symmetric_difference() -> None:
    assert Set(Int(1), Int(2)) ^ Set(Int(2), Int(3)) == Set(Int(1), Int(3))


def test_dunder_or_with_frozenset_returns_set() -> None:
    # CPython: result takes the left operand's type.
    result = Set(Int(1), Int(2)) | FrozenSet(Int(3))
    assert isinstance(result, Set)
    assert result == Set(Int(1), Int(2), Int(3))


def test_dunder_and_with_frozenset() -> None:
    assert Set(Int(1), Int(2), Int(3)) & FrozenSet(Int(2), Int(3), Int(4)) == Set(
        Int(2), Int(3)
    )


def test_dunder_sub_with_frozenset() -> None:
    assert Set(Int(1), Int(2), Int(3)) - FrozenSet(Int(2)) == Set(Int(1), Int(3))


def test_dunder_xor_with_frozenset() -> None:
    assert Set(Int(1), Int(2)) ^ FrozenSet(Int(2), Int(3)) == Set(Int(1), Int(3))


def test_dunder_or_with_non_set_raises() -> None:
    with pytest.raises(TypeError):
        Set(Int(1)) | Int(2)


def test_inplace_or_mutates_in_place() -> None:
    # CPython: ``s |= other`` keeps ``s``'s identity, so aliases see the change.
    s = Set(Int(1), Int(2))
    alias = s
    s |= Set(Int(3))
    assert s is alias
    assert alias == Set(Int(1), Int(2), Int(3))


def test_inplace_and_mutates_in_place() -> None:
    s = Set(Int(1), Int(2), Int(3))
    alias = s
    s &= Set(Int(2), Int(3), Int(4))
    assert s is alias
    assert alias == Set(Int(2), Int(3))


def test_inplace_sub_mutates_in_place() -> None:
    s = Set(Int(1), Int(2), Int(3))
    alias = s
    s -= Set(Int(2))
    assert s is alias
    assert alias == Set(Int(1), Int(3))


def test_inplace_xor_mutates_in_place() -> None:
    s = Set(Int(1), Int(2))
    alias = s
    s ^= Set(Int(2), Int(3))
    assert s is alias
    assert alias == Set(Int(1), Int(3))


def test_inplace_or_with_frozenset() -> None:
    s = Set(Int(1), Int(2))
    s |= FrozenSet(Int(3))
    assert s == Set(Int(1), Int(2), Int(3))


def test_inplace_or_with_non_set_raises() -> None:
    with pytest.raises(TypeError):
        s = Set(Int(1))
        s |= Int(2)


def test_lt_proper_subset_true() -> None:
    assert (Set(Int(1), Int(2)) < Set(Int(1), Int(2), Int(3))) is true


def test_lt_equal_sets_false() -> None:
    # ``<`` is a *proper* subset: equal sets are not less-than.
    assert (Set(Int(1), Int(2)) < Set(Int(1), Int(2))) is false


def test_le_subset_true() -> None:
    assert (Set(Int(1), Int(2)) <= Set(Int(1), Int(2))) is true


def test_gt_proper_superset_true() -> None:
    assert (Set(Int(1), Int(2), Int(3)) > Set(Int(1), Int(2))) is true


def test_ge_superset_true() -> None:
    assert (Set(Int(1), Int(2)) >= Set(Int(1), Int(2))) is true


def test_lt_unrelated_sets_false() -> None:
    # Disjoint/unrelated sets compare ``False`` (not an error) in CPython.
    assert (Set(Int(1), Int(2)) < Set(Int(3), Int(4))) is false


def test_comparison_mixes_with_frozenset() -> None:
    # CPython lets ``set`` and ``frozenset`` mix under subset/superset tests.
    assert (Set(Int(1), Int(2), Int(3)) > FrozenSet(Int(1), Int(2))) is true
    assert (FrozenSet(Int(1), Int(2)) < Set(Int(1), Int(2), Int(3))) is true


def test_comparison_with_non_set_raises() -> None:
    with pytest.raises(TypeError):
        Set(Int(1)) < Int(2)


def test_set_inplace_ops_against_foreign_are_notimplemented() -> None:
    # `&=`, `-=`, `^=` against a non-set operand answer NotImplemented so
    # CPython falls back and raises its faithful TypeError.
    from poop.types.int import Int
    from poop.types.set import Set

    for op in ("__iand__", "__isub__", "__ixor__"):
        assert getattr(Set(Int(1)), op)(Int(3)) is NotImplemented


def test_set_subset_superset_against_foreign_raise() -> None:
    import pytest

    from poop.types.int import Int
    from poop.types.set import Set

    for op in (
        lambda: Set(Int(1)) <= Int(3),
        lambda: Set(Int(1)) >= Int(3),
        lambda: Set(Int(1)) > Int(3),
    ):
        with pytest.raises(TypeError):
            op()
