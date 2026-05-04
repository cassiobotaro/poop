import pytest

from poop.parser import parse
from poop.transformers.int import IntTransformer
from poop.transformers.set import SetTransformer, _poop_set
from poop.types.boolean import false, true
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


def test_add_returns_self() -> None:
    s = Set()
    result = s.add(Int(1))
    assert result is s


def test_add_increases_len() -> None:
    s = Set()
    s.add(Int(1))
    s.add(Int(2))
    assert s.len() == Int(2)


def test_add_duplicate_keeps_unique() -> None:
    s = Set(Int(1))
    s.add(Int(1))
    assert s.len() == Int(1)


def test_remove_returns_self() -> None:
    s = Set(Int(1))
    result = s.remove(Int(1))
    assert result is s


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


def test_map_returns_set() -> None:
    s = Set(Int(1), Int(2))
    result = s.map(lambda x: x)
    assert isinstance(result, Set)


def test_map_transforms_elements() -> None:
    s = Set(Int(2))
    result = s.map(lambda x: Int(x._value * 2))
    assert result.includes(Int(4)) is true


def test_filter_keeps_matching() -> None:
    s = Set(Int(1), Int(2), Int(3), Int(4))
    result = s.filter(lambda x: x._value % 2 == 0)
    assert result.len() == Int(2)
    assert result.includes(Int(2)) is true
    assert result.includes(Int(4)) is true


def test_filter_false_keeps_non_matching() -> None:
    s = Set(Int(1), Int(2), Int(3))
    result = s.filter_false(lambda x: x._value % 2 == 0)
    assert result.len() == Int(2)


def test_find_returns_matching_element() -> None:
    s = Set(Int(1), Int(2), Int(3))
    result = s.find(lambda x: x._value > 2)
    assert result == Int(3)


def test_find_returns_none_when_not_found() -> None:
    s = Set(Int(1), Int(2))
    assert s.find(lambda x: x._value > 99) is none


def test_reduce_accumulates() -> None:
    s = Set(Int(1), Int(2), Int(3))
    result = s.reduce(Int(0), lambda acc, x: Int(acc._value + x._value))
    assert result == Int(6)


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


def test_discard_returns_self() -> None:
    s = Set(Int(1))
    assert s.discard(Int(1)) is s


def test_clear_empties_set() -> None:
    s = Set(Int(1), Int(2))
    s.clear()
    assert s.len() == Int(0)


def test_clear_returns_self() -> None:
    s = Set(Int(1))
    assert s.clear() is s


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


def test_update_returns_self() -> None:
    s = Set(Int(1))
    assert s.update(Set(Int(2))) is s


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
