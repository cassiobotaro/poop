import pytest

from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_empty_tuple() -> None:
    assert Tuple().len() == Int(0)


def test_len() -> None:
    assert Tuple(Int(1), Int(2), Int(3)).len() == Int(3)


def test_dunder_len() -> None:
    assert len(Tuple(Int(1), Int(2))) == 2


def test_at() -> None:
    t = Tuple(Int(10), Int(20), Int(30))
    assert t.at(Int(0)) == Int(10)
    assert t.at(Int(2)) == Int(30)


def test_at_returns_element() -> None:
    t = Tuple(Int(10), Int(20))
    assert t.at(Int(1)) == Int(20)


def test_includes_true() -> None:
    assert Tuple(Int(1), Int(2), Int(3)).includes(Int(2)) is true


def test_includes_false() -> None:
    assert Tuple(Int(1), Int(3)).includes(Int(2)) is false


def test_contains_dunder() -> None:
    t = Tuple(Int(1), Int(2))
    assert Int(1) in t
    assert Int(9) not in t


def test_do_iterates() -> None:
    results: list[Int] = []
    Tuple(Int(1), Int(2), Int(3)).do(lambda x: results.append(x))
    assert results == [Int(1), Int(2), Int(3)]


def test_map_transforms_elements() -> None:
    result = Tuple(Int(1), Int(2), Int(3)).map(lambda x: x + Int(10))
    assert Tuple(*result) == Tuple(Int(11), Int(12), Int(13))


def test_map_returns_lazy_map() -> None:
    from poop.types.map import Map

    assert isinstance(Tuple(Int(1)).map(lambda x: x), Map)


def test_filter_keeps_matching() -> None:
    result = Tuple(Int(1), Int(2), Int(3), Int(4)).filter(
        lambda x: x % Int(2) == Int(0)
    )
    assert Tuple(*result) == Tuple(Int(2), Int(4))


def test_filter_false_keeps_non_matching() -> None:
    result = Tuple(Int(1), Int(2), Int(3), Int(4)).filter_false(
        lambda x: x % Int(2) == Int(0)
    )
    assert Tuple(*result) == Tuple(Int(1), Int(3))


def test_detect_finds_first() -> None:
    result = Tuple(Int(1), Int(2), Int(3)).find(lambda x: x > Int(1))
    assert result == Int(2)


def test_detect_returns_none_when_not_found() -> None:
    result = Tuple(Int(1), Int(2)).find(lambda x: x > Int(10))
    assert result is none


def test_do_returns_none() -> None:
    assert Tuple(Int(1), Int(2)).do(lambda x: x) is none


def test_reduce_sum() -> None:
    assert Tuple(Int(1), Int(2), Int(3), Int(4)).reduce(
        Int(0), lambda acc, x: acc + x
    ) == Int(10)


def test_sum_returns_total() -> None:
    assert Tuple(Int(1), Int(2), Int(3)).sum() == Int(6)


def test_sum_empty_returns_zero() -> None:
    assert Tuple().sum() == Int(0)


def test_sum_with_start() -> None:
    assert Tuple(Int(1), Int(2), Int(3)).sum(Int(10)) == Int(16)


def test_sum_empty_with_start_returns_start() -> None:
    assert Tuple().sum(Int(5)) == Int(5)


def test_all_true() -> None:
    assert Tuple(Int(2), Int(4), Int(6)).all(lambda x: x % Int(2) == Int(0)) is true


def test_all_false() -> None:
    assert Tuple(Int(1), Int(2), Int(3)).all(lambda x: x % Int(2) == Int(0)) is false


def test_any_true() -> None:
    assert Tuple(Int(1), Int(2), Int(3)).any(lambda x: x % Int(2) == Int(0)) is true


def test_any_false() -> None:
    assert Tuple(Int(1), Int(3)).any(lambda x: x % Int(2) == Int(0)) is false


def test_iter() -> None:
    items = list(Tuple(Int(1), Int(2), Int(3)))
    assert items == [Int(1), Int(2), Int(3)]


def test_eq_equal_tuples() -> None:
    assert Tuple(Int(1), Int(2)) == Tuple(Int(1), Int(2))


def test_eq_different_tuples() -> None:
    assert (Tuple(Int(1), Int(2)) == Tuple(Int(1), Int(3))) is false


def test_ne_different_tuples() -> None:
    assert (Tuple(Int(1)) != Tuple(Int(2))) is true


def test_lt_lexicographic_first_position_decides() -> None:
    assert (Tuple(Int(1), Int(99)) < Tuple(Int(2), Int(0))) is true


def test_lt_lexicographic_second_position_decides() -> None:
    assert (Tuple(Int(1), Int(2)) < Tuple(Int(1), Int(3))) is true


def test_lt_equal_returns_false() -> None:
    assert (Tuple(Int(1), Int(2)) < Tuple(Int(1), Int(2))) is false


def test_le_equal_returns_true() -> None:
    assert (Tuple(Int(1), Int(2)) <= Tuple(Int(1), Int(2))) is true


def test_gt_lexicographic() -> None:
    assert (Tuple(Int(3), Int(0)) > Tuple(Int(1), Int(99))) is true


def test_ge_equal_returns_true() -> None:
    assert (Tuple(Int(1), Int(2)) >= Tuple(Int(1), Int(2))) is true


def test_lt_shorter_prefix_is_smaller() -> None:
    assert (Tuple(Int(1), Int(2)) < Tuple(Int(1), Int(2), Int(0))) is true


def test_str_empty() -> None:
    assert str(Tuple()) == "()"


def test_str_single_element() -> None:
    assert str(Tuple(Int(1))) == "(1,)"


def test_str_multiple_elements() -> None:
    assert str(Tuple(Int(1), Int(2))) == "(1, 2)"


def test_hashable() -> None:
    t = Tuple(Int(1), Int(2))
    assert isinstance(hash(t), int)


def test_hashable_usable_in_set() -> None:
    t1 = Tuple(Int(1), Int(2))
    t2 = Tuple(Int(1), Int(2))
    s = {t1, t2}
    assert len(s) == 1


def test_immutable_no_add() -> None:
    t = Tuple(Int(1))
    assert not hasattr(t, "add")


def test_no_mutate_original() -> None:
    t = Tuple(Int(1), Int(2), Int(3))
    t.filter(lambda x: x > Int(1))
    assert t == Tuple(Int(1), Int(2), Int(3))


def test_not_equal_to_list() -> None:
    assert (Tuple(Int(1)) == List(Int(1))) is false


def test_repr_equals_str() -> None:
    assert repr(Tuple(Int(1), Int(2))) == str(Tuple(Int(1), Int(2)))


def test_sorted_ascending() -> None:
    t = Tuple(Int(3), Int(1), Int(2))
    assert t.sorted() == Tuple(Int(1), Int(2), Int(3))


def test_sorted_returns_new_tuple() -> None:
    t = Tuple(Int(3), Int(1), Int(2))
    result = t.sorted()
    assert isinstance(result, Tuple)
    assert t == Tuple(Int(3), Int(1), Int(2))


def test_sorted_empty() -> None:
    assert Tuple().sorted() == Tuple()


def test_sorted_with_key() -> None:
    t = Tuple(Int(-3), Int(1), Int(-2))
    result = t.sorted(key=lambda x: x.abs())  # ty: ignore[unresolved-attribute]
    assert result == Tuple(Int(1), Int(-2), Int(-3))


def test_sorted_reverse() -> None:
    t = Tuple(Int(1), Int(3), Int(2))
    assert t.sorted(reverse=true) == Tuple(Int(3), Int(2), Int(1))


def test_reversed_returns_new_tuple() -> None:
    t = Tuple(Int(1), Int(2), Int(3))
    result = t.reversed()
    assert isinstance(result, Tuple)
    assert result == Tuple(Int(3), Int(2), Int(1))


def test_reversed_does_not_mutate() -> None:
    t = Tuple(Int(1), Int(2), Int(3))
    t.reversed()
    assert t == Tuple(Int(1), Int(2), Int(3))


def test_reversed_empty() -> None:
    assert Tuple().reversed() == Tuple()


def test_count_found() -> None:
    assert Tuple(Int(1), Int(2), Int(1), Int(3)).count(Int(1)) == Int(2)


def test_count_not_found() -> None:
    assert Tuple(Int(1), Int(2)).count(Int(9)) == Int(0)


def test_count_empty() -> None:
    assert Tuple().count(Int(1)) == Int(0)


def test_index_first_occurrence() -> None:
    assert Tuple(Int(10), Int(20), Int(10)).index(Int(10)) == Int(0)


def test_index_middle() -> None:
    assert Tuple(Int(1), Int(2), Int(3)).index(Int(2)) == Int(1)


def test_index_not_found_raises() -> None:
    with pytest.raises(ValueError):
        Tuple(Int(1), Int(2)).index(Int(9))


def test_index_with_start() -> None:
    assert Tuple(Int(10), Int(20), Int(10)).index(Int(10), Int(1)) == Int(2)


def test_index_with_start_and_stop() -> None:
    ts = Tuple(Int(5), Int(10), Int(5), Int(10))
    assert ts.index(Int(10), Int(2), Int(4)) == Int(3)


def test_slice_with_step() -> None:
    t = Tuple(Int(0), Int(1), Int(2), Int(3), Int(4))
    assert t.slice(Int(0), Int(5), Int(2)) == Tuple(Int(0), Int(2), Int(4))


def test_add_concatenates() -> None:
    assert Tuple(Int(1), Int(2)) + Tuple(Int(3), Int(4)) == Tuple(
        Int(1), Int(2), Int(3), Int(4)
    )


def test_add_foreign_operand_raises_type_error() -> None:
    # CPython raises TypeError, not AttributeError, when the right operand
    # of `+` is not a tuple.
    with pytest.raises(TypeError):
        Tuple(Int(1)) + Int(2)


def test_mul_repeats() -> None:
    assert Tuple(Int(1), Int(2)) * Int(2) == Tuple(Int(1), Int(2), Int(1), Int(2))


def test_mul_by_boolean_folds_to_int() -> None:
    # bool is an int subclass in CPython: (1, 2) * True == (1, 2).
    assert Tuple(Int(1), Int(2)) * true == Tuple(Int(1), Int(2))
    assert Tuple(Int(1), Int(2)) * false == Tuple()


def test_rmul_by_boolean_folds_to_int() -> None:
    assert true * Tuple(Int(1), Int(2)) == Tuple(Int(1), Int(2))
    assert false * Tuple(Int(1), Int(2)) == Tuple()


def test_ne_with_non_tuple_returns_true() -> None:
    assert Tuple(Int(1)).__ne__(List(Int(1))) is true


def test_tuple_usable_as_dict_key() -> None:
    key = Tuple(Int(1), Int(2))
    d = Dict().at_put(key, Str("v"))

    assert d.at(Tuple(Int(1), Int(2))) == Str("v")
    assert d.includes(Tuple(Int(1), Int(2))) is true
    assert d.includes(Tuple(Int(1), Int(3))) is false


def test_tuple_hash_matches_for_equal_tuples() -> None:
    assert hash(Tuple(Int(1), Int(2))) == hash(Tuple(Int(1), Int(2)))


def test_print_accepts_poop_none_kwargs(capsys: pytest.CaptureFixture[str]) -> None:
    Tuple(Int(1), Int(2)).print(sep=none, end=none, flush=none)
    captured = capsys.readouterr()
    assert captured.out == "1 2\n"


def test_rmul_returns_repeated_tuple() -> None:
    assert Tuple(Int(1), Int(2)).__rmul__(Int(3)) == Tuple(
        Int(1), Int(2), Int(1), Int(2), Int(1), Int(2)
    )


def test_ordering_with_foreign_operand_raises_typeerror() -> None:
    # Proposal 164: a foreign operand answers CPython's TypeError, not a
    # leaking AttributeError from a missing `other._items`.
    with pytest.raises(TypeError):
        _ = Tuple(Int(1)) < Int(2)
    with pytest.raises(TypeError):
        _ = Tuple(Int(1)) >= List(Int(2))


def test_tuple_gt_against_foreign_raises() -> None:
    import pytest

    from poop.types.int import Int
    from poop.types.tuple import Tuple

    with pytest.raises(TypeError):
        _ = Tuple(Int(1)) > Int(1)


def test_at_accepts_a_boolean_index() -> None:
    assert Tuple(Int(10), Int(20)).at(true) == Int(20)


def test_at_with_a_foreign_index_is_faithful_not_a_value_leak() -> None:
    with pytest.raises(TypeError) as info:
        Tuple(Int(1)).at(List(Int(0)))  # ty: ignore[invalid-argument-type]
    assert "_value" not in str(info.value)


def test_repr_of_a_tuple_holding_a_list_that_holds_it_answers_the_ellipsis() -> None:
    # A tuple is immutable but not acyclic. CPython prints `([(...)],)`.
    xs = List()
    t = Tuple(xs)
    xs.append(t)
    assert str(t) == "([(...)],)"


def test_sorted_takes_key_only_by_keyword() -> None:
    with pytest.raises(TypeError):
        Tuple(Int(2), Int(1)).sorted(lambda x: x)  # ty: ignore[too-many-positional-arguments]


def test_sorted_reads_a_none_key_as_absent() -> None:
    assert Tuple(Int(2), Int(1)).sorted(key=none) == Tuple(Int(1), Int(2))
