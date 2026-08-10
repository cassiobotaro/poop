import pytest

from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.slice import Slice
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_empty_list() -> None:
    assert List().len() == Int(0)


def test_len() -> None:
    assert List(Int(1), Int(2), Int(3)).len() == Int(3)


def test_dunder_len() -> None:
    assert len(List(Int(1), Int(2))) == 2


def test_at() -> None:
    lst = List(Int(10), Int(20), Int(30))
    assert lst.at(Int(0)) == Int(10)
    assert lst.at(Int(2)) == Int(30)


def test_at_returns_element() -> None:
    lst = List(Int(10), Int(20))
    assert lst.at(Int(1)) == Int(20)


def test_at_with_slice_returns_sublist() -> None:
    lst = List(Int(10), Int(20), Int(30), Int(40))
    assert lst.at(Slice(Int(1), Int(3))) == List(Int(20), Int(30))


def test_at_with_slice_matches_slice_method() -> None:
    lst = List(Int(0), Int(1), Int(2), Int(3), Int(4))
    assert lst.at(Slice(Int(0), Int(5), Int(2))) == lst.slice(Int(0), Int(5), Int(2))


def test_includes_true() -> None:
    assert List(Int(1), Int(2), Int(3)).includes(Int(2)) is true


def test_includes_false() -> None:
    assert List(Int(1), Int(3)).includes(Int(2)) is false


def test_contains_dunder() -> None:
    lst = List(Int(1), Int(2))
    assert Int(1) in lst
    assert Int(9) not in lst


def test_do_iterates() -> None:
    results: list[Int] = []
    List(Int(1), Int(2), Int(3)).do(lambda x: results.append(x))
    assert results == [Int(1), Int(2), Int(3)]


def test_map_transforms_elements() -> None:
    result = List(Int(1), Int(2), Int(3)).map(lambda x: x + Int(10))
    assert List(*result) == List(Int(11), Int(12), Int(13))


def test_map_returns_lazy_map() -> None:
    from poop.types.map import Map

    assert isinstance(List(Int(1)).map(lambda x: x), Map)


def test_filter_keeps_matching() -> None:
    result = List(Int(1), Int(2), Int(3), Int(4)).filter(lambda x: x % Int(2) == Int(0))
    assert List(*result) == List(Int(2), Int(4))


def test_filter_false_keeps_non_matching() -> None:
    result = List(Int(1), Int(2), Int(3), Int(4)).filter_false(
        lambda x: x % Int(2) == Int(0)
    )
    assert List(*result) == List(Int(1), Int(3))


def test_detect_finds_first() -> None:
    result = List(Int(1), Int(2), Int(3)).find(lambda x: x > Int(1))
    assert result == Int(2)


def test_detect_returns_none_when_not_found() -> None:
    result = List(Int(1), Int(2)).find(lambda x: x > Int(10))
    assert result is none


def test_do_returns_none() -> None:
    assert List(Int(1), Int(2)).do(lambda x: x) is none


def test_reduce_sum() -> None:
    assert List(Int(1), Int(2), Int(3), Int(4)).reduce(
        Int(0), lambda acc, x: acc + x
    ) == Int(10)


def test_reduce_product() -> None:
    assert List(Int(1), Int(2), Int(3), Int(4)).reduce(
        Int(1), lambda acc, x: acc * x
    ) == Int(24)


def test_reduce_empty_returns_init() -> None:
    assert List().reduce(Int(0), lambda acc, x: acc + x) == Int(0)


def test_sum_returns_total() -> None:
    assert List(Int(1), Int(2), Int(3)).sum() == Int(6)


def test_sum_empty_returns_zero() -> None:
    assert List().sum() == Int(0)


def test_sum_with_start() -> None:
    assert List(Int(1), Int(2), Int(3)).sum(Int(10)) == Int(16)


def test_sum_empty_with_start_returns_start() -> None:
    assert List().sum(Int(5)) == Int(5)


def test_all_true() -> None:
    assert List(Int(2), Int(4), Int(6)).all(lambda x: x % Int(2) == Int(0)) is true


def test_all_false() -> None:
    assert List(Int(1), Int(2), Int(3)).all(lambda x: x % Int(2) == Int(0)) is false


def test_any_true() -> None:
    assert List(Int(1), Int(2), Int(3)).any(lambda x: x % Int(2) == Int(0)) is true


def test_any_false() -> None:
    assert List(Int(1), Int(3)).any(lambda x: x % Int(2) == Int(0)) is false


def test_append_adds_element() -> None:
    lst = List(Int(1), Int(2))
    lst.append(Int(3))
    assert lst == List(Int(1), Int(2), Int(3))


def test_append_returns_none() -> None:
    lst = List(Int(1))
    assert lst.append(Int(2)) is none


def test_pop_returns_last_element() -> None:
    lst = List(Int(10), Int(20), Int(30))
    assert lst.pop() == Int(30)


def test_pop_removes_last_element() -> None:
    lst = List(Int(10), Int(20), Int(30))
    lst.pop()
    assert lst.len() == Int(2)
    assert lst.at(Int(-1)) == Int(20)


def test_pop_successive_calls() -> None:
    lst = List(Int(1), Int(2), Int(3))
    assert lst.pop() == Int(3)
    assert lst.pop() == Int(2)
    assert lst.pop() == Int(1)


def test_iter() -> None:
    items = list(List(Int(1), Int(2), Int(3)))
    assert items == [Int(1), Int(2), Int(3)]


def test_eq_equal_lists() -> None:
    assert List(Int(1), Int(2)) == List(Int(1), Int(2))


def test_eq_different_lists() -> None:
    assert (List(Int(1), Int(2)) == List(Int(1), Int(3))) is false


def test_ne_different_lists() -> None:
    assert (List(Int(1)) != List(Int(2))) is true


def test_str_representation() -> None:
    assert str(List(Int(1), Int(2))) == "[1, 2]"


def test_str_empty() -> None:
    assert str(List()) == "[]"


def test_not_hashable() -> None:
    with pytest.raises(TypeError):
        hash(List())


def test_repr_equals_str() -> None:
    assert repr(List(Int(1), Int(2))) == str(List(Int(1), Int(2)))


def test_sorted_ascending() -> None:
    lst = List(Int(3), Int(1), Int(2))
    assert lst.sorted() == List(Int(1), Int(2), Int(3))


def test_sorted_returns_new_list() -> None:
    lst = List(Int(3), Int(1), Int(2))
    result = lst.sorted()
    assert isinstance(result, List)
    assert lst == List(Int(3), Int(1), Int(2))


def test_sorted_empty() -> None:
    assert List().sorted() == List()


def test_sorted_with_key() -> None:
    lst = List(Int(-3), Int(1), Int(-2))
    result = lst.sorted(key=lambda x: x.abs())  # ty: ignore[unresolved-attribute]
    assert result == List(Int(1), Int(-2), Int(-3))


def test_sorted_reverse() -> None:
    lst = List(Int(1), Int(3), Int(2))
    assert lst.sorted(reverse=true) == List(Int(3), Int(2), Int(1))


def test_sorted_reverse_with_key() -> None:
    lst = List(Int(-3), Int(1), Int(-2))
    result = lst.sorted(key=lambda x: x.abs(), reverse=true)  # ty: ignore[unresolved-attribute]
    assert result == List(Int(-3), Int(-2), Int(1))


def test_reversed_returns_new_list() -> None:
    lst = List(Int(1), Int(2), Int(3))
    result = lst.reversed()
    assert isinstance(result, List)
    assert result == List(Int(3), Int(2), Int(1))


def test_reversed_does_not_mutate() -> None:
    lst = List(Int(1), Int(2), Int(3))
    lst.reversed()
    assert lst == List(Int(1), Int(2), Int(3))


def test_reversed_empty() -> None:
    assert List().reversed() == List()


def test_clear_empties_list() -> None:
    lst = List(Int(1), Int(2), Int(3))
    lst.clear()
    assert lst.len() == Int(0)


def test_clear_returns_none() -> None:
    lst = List(Int(1))
    assert lst.clear() is none


def test_copy_returns_new_list() -> None:
    lst = List(Int(1), Int(2))
    c = lst.copy()
    assert c is not lst
    assert c == lst


def test_copy_is_shallow() -> None:
    lst = List(Int(1), Int(2))
    c = lst.copy()
    lst.clear()
    assert c.len() == Int(2)


def test_count_found() -> None:
    assert List(Int(1), Int(2), Int(1)).count(Int(1)) == Int(2)


def test_count_not_found() -> None:
    assert List(Int(1), Int(2)).count(Int(9)) == Int(0)


def test_extend_appends_all() -> None:
    lst = List(Int(1), Int(2))
    lst.extend(List(Int(3), Int(4)))
    assert lst == List(Int(1), Int(2), Int(3), Int(4))


def test_extend_returns_none() -> None:
    lst = List(Int(1))
    assert lst.extend(List(Int(2))) is none


def test_index_found() -> None:
    assert List(Int(10), Int(20), Int(30)).index(Int(20)) == Int(1)


def test_index_with_start() -> None:
    assert List(Int(10), Int(20), Int(10)).index(Int(10), Int(1)) == Int(2)


def test_index_with_start_and_stop() -> None:
    xs = List(Int(5), Int(10), Int(5), Int(10))
    assert xs.index(Int(10), Int(2), Int(4)) == Int(3)


def test_index_not_found_raises() -> None:
    with pytest.raises(ValueError):
        List(Int(1), Int(2)).index(Int(9))


def test_index_honours_stop_without_start() -> None:
    # `stop` was dropped whenever `start` was absent, so this answered 2 —
    # a match from outside the bound the reader handed it.
    with pytest.raises(ValueError):
        List(Int(1), Int(2), Int(3)).index(Int(3), stop=Int(1))


def test_index_reads_a_none_stop_as_the_end() -> None:
    # `_opt_int(stop, 0)` read an explicit `none` as "stop at 0", which makes
    # every search fail.
    xs = List(Int(1), Int(2), Int(3))
    assert xs.index(Int(3), none, none) == Int(2)
    assert xs.index(Int(3), Int(1), none) == Int(2)


def test_index_with_a_stop_that_excludes_the_only_match() -> None:
    xs = List(Int(5), Int(10), Int(5), Int(10))
    with pytest.raises(ValueError):
        xs.index(Int(10), Int(0), Int(1))


def test_insert_at_position() -> None:
    lst = List(Int(1), Int(3))
    lst.insert(Int(1), Int(2))
    assert lst == List(Int(1), Int(2), Int(3))


def test_insert_returns_none() -> None:
    lst = List(Int(1))
    assert lst.insert(Int(0), Int(0)) is none


def test_remove_first_occurrence() -> None:
    lst = List(Int(1), Int(2), Int(1))
    lst.remove(Int(1))
    assert lst == List(Int(2), Int(1))


def test_remove_returns_none() -> None:
    lst = List(Int(1))
    assert lst.remove(Int(1)) is none


def test_remove_not_found_raises() -> None:
    with pytest.raises(ValueError):
        List(Int(1)).remove(Int(9))


def test_reverse_mutates_in_place() -> None:
    lst = List(Int(1), Int(2), Int(3))
    lst.reverse()
    assert lst == List(Int(3), Int(2), Int(1))


def test_reverse_returns_none() -> None:
    lst = List(Int(1), Int(2))
    assert lst.reverse() is none


def test_sort_mutates_in_place() -> None:
    lst = List(Int(3), Int(1), Int(2))
    lst.sort()
    assert lst == List(Int(1), Int(2), Int(3))


def test_sort_returns_none() -> None:
    lst = List(Int(3), Int(1))
    assert lst.sort() is none


def test_sort_with_key() -> None:
    lst = List(Int(-3), Int(1), Int(-2))
    lst.sort(key=lambda x: x.abs())  # ty: ignore[unresolved-attribute]
    assert lst == List(Int(1), Int(-2), Int(-3))


def test_sort_reverse() -> None:
    lst = List(Int(1), Int(2), Int(3))
    lst.sort(reverse=true)
    assert lst == List(Int(3), Int(2), Int(1))


def test_slice_with_step() -> None:
    assert List(Int(0), Int(1), Int(2), Int(3), Int(4)).slice(
        Int(0), Int(5), Int(2)
    ) == List(Int(0), Int(2), Int(4))


def test_add_concatenates() -> None:
    assert List(Int(1), Int(2)) + List(Int(3), Int(4)) == List(
        Int(1), Int(2), Int(3), Int(4)
    )


def test_add_foreign_operand_raises_type_error() -> None:
    # CPython raises TypeError, not AttributeError, when the right operand
    # of `+` is not a list.
    with pytest.raises(TypeError):
        List(Int(1)) + Int(2)


def test_mul_repeats() -> None:
    assert List(Int(1), Int(2)) * Int(2) == List(Int(1), Int(2), Int(1), Int(2))


def test_mul_by_boolean_folds_to_int() -> None:
    # bool is an int subclass in CPython: [1, 2] * True == [1, 2].
    assert List(Int(1), Int(2)) * true == List(Int(1), Int(2))
    assert List(Int(1), Int(2)) * false == List()


def test_rmul_by_boolean_folds_to_int() -> None:
    assert true * List(Int(1), Int(2)) == List(Int(1), Int(2))
    assert false * List(Int(1), Int(2)) == List()


def test_eq_with_non_list_returns_false() -> None:
    assert List(Int(1)).__eq__(Int(1)) is false


def test_ne_with_non_list_returns_true() -> None:
    assert List(Int(1)).__ne__(Int(1)) is true


# Lexicographic ordering — proposal 150


def test_list_lt_lexicographic() -> None:
    assert (List(Int(1), Int(2)) < List(Int(1), Int(3))) is true
    assert (List(Int(1), Int(3)) < List(Int(1), Int(2))) is false


def test_list_le_ge_gt() -> None:
    assert (List(Int(1), Int(2)) <= List(Int(1), Int(2))) is true
    assert (List(Int(2)) > List(Int(1), Int(9))) is true
    assert (List(Int(1), Int(9)) >= List(Int(1), Int(9))) is true


def test_sorted_over_nested_lists() -> None:
    nested = List(List(Int(2), Int(1)), List(Int(1), Int(9)))
    assert nested.sorted() == List(List(Int(1), Int(9)), List(Int(2), Int(1)))


def test_print_accepts_poop_none_kwargs(capsys: pytest.CaptureFixture[str]) -> None:
    List(Int(1), Int(2)).print(sep=none, end=none, flush=none)
    captured = capsys.readouterr()
    assert captured.out == "1 2\n"


# --- New: optional parameters (proposals 33 & 39, v1.2.0) ---


def test_pop_at_index() -> None:
    lst = List(Int(1), Int(2), Int(3))
    assert lst.pop(Int(0)) == Int(1)
    assert lst == List(Int(2), Int(3))


def test_pop_with_poop_none_index() -> None:
    lst = List(Int(1), Int(2))
    assert lst.pop(none) == Int(2)


def test_rmul_returns_repeated_list() -> None:
    assert List(Int(1), Int(2)).__rmul__(Int(3)) == List(
        Int(1), Int(2), Int(1), Int(2), Int(1), Int(2)
    )


def test_ordering_with_foreign_operand_raises_typeerror() -> None:
    # Proposal 164: a foreign operand answers CPython's TypeError, not a
    # leaking AttributeError from a missing `other._items`.
    with pytest.raises(TypeError):
        _ = List(Int(1)) < Int(2)
    with pytest.raises(TypeError):
        _ = List(Int(1)) >= Int(2)


def test_inplace_add_mutates_in_place() -> None:
    # CPython: ``xs += ys`` keeps ``xs``'s identity, so aliases see the change.
    xs = List(Int(1), Int(2))
    alias = xs
    xs += List(Int(3))
    assert xs is alias
    assert alias == List(Int(1), Int(2), Int(3))


def test_inplace_add_accepts_any_iterable() -> None:
    # CPython's ``list.__iadd__`` is ``list.extend`` — it takes any iterable,
    # unlike ``+``, which stays list-only.
    xs = List(Int(1))
    xs += Tuple(Int(2), Int(3))
    assert xs == List(Int(1), Int(2), Int(3))


def test_inplace_mul_mutates_in_place() -> None:
    # CPython: ``xs *= n`` repeats in place and keeps ``xs``'s identity.
    xs = List(Int(1), Int(2))
    alias = xs
    xs *= Int(2)
    assert xs is alias
    assert alias == List(Int(1), Int(2), Int(1), Int(2))


def test_inplace_mul_by_zero_clears_in_place() -> None:
    xs = List(Int(1), Int(2))
    alias = xs
    xs *= Int(0)
    assert xs is alias
    assert alias == List()


def test_inplace_mul_by_non_int_raises_typeerror() -> None:
    with pytest.raises(TypeError):
        xs = List(Int(1))
        xs *= Str("2")


def test_list_gt_against_foreign_raises() -> None:
    import pytest

    from poop.types.int import Int
    from poop.types.list import List

    with pytest.raises(TypeError):
        _ = List(Int(1)) > Int(1)


def test_at_accepts_a_boolean_index() -> None:
    # CPython: [10, 20][True] is 20, bool being an int subclass.
    assert List(Int(10), Int(20)).at(true) == Int(20)
    assert List(Int(10), Int(20)).at(false) == Int(10)


def test_at_with_a_foreign_index_is_faithful_not_a_value_leak() -> None:
    with pytest.raises(TypeError) as info:
        List(Int(1)).at(List(Int(0)))  # ty: ignore[invalid-argument-type]
    assert "_value" not in str(info.value)


def test_insert_and_pop_accept_a_boolean_index() -> None:
    xs = List(Int(1), Int(3))
    xs.insert(true, Int(2))
    assert xs == List(Int(1), Int(2), Int(3))
    assert xs.pop(true) == Int(2)


def test_repr_of_a_self_referential_list_answers_the_ellipsis() -> None:
    # CPython prints `[1, [...]]`; recursing until the stack gave out reported
    # a RecursionError about POOP's internals to a program that only printed.
    xs = List(Int(1))
    xs.append(xs)
    assert str(xs) == "[1, [...]]"
    assert repr(xs) == "[1, [...]]"


def test_repr_of_a_mutually_referential_pair_answers_the_ellipsis() -> None:
    outer = List()
    inner = List(outer)
    outer.append(inner)
    assert str(outer) == "[[[...]]]"


def test_sorted_and_sort_take_key_only_by_keyword() -> None:
    # CPython: `sorted(iterable, /, *, key, reverse)`. Positionally a block is
    # indistinguishable from any other value.
    with pytest.raises(TypeError):
        List(Int(2), Int(1)).sorted(lambda x: x)  # ty: ignore[too-many-positional-arguments]
    with pytest.raises(TypeError):
        List(Int(2), Int(1)).sort(lambda x: x)  # ty: ignore[too-many-positional-arguments]


def test_sorted_and_sort_read_a_none_key_as_absent() -> None:
    # POOP's `None` is a NoneClass instance, so `is None` read it as a
    # comparison block and answered `'NoneType' object is not callable`.
    assert List(Int(2), Int(1)).sorted(key=none) == List(Int(1), Int(2))
    xs = List(Int(2), Int(1))
    xs.sort(key=none)
    assert xs == List(Int(1), Int(2))


# --- the write half of `at` ---
#
# `no_subscript` refuses `xs[0] = 9` and names a substitute; there was none.
# `Dict` and `ByteArray` both answer `at_put`, and the collection between them
# — indexable, mutable, ordered — could not replace an element at all.


def test_at_put_replaces_the_element() -> None:
    xs = List(Int(1), Int(2))
    xs.at_put(Int(0), Int(9))
    assert xs == List(Int(9), Int(2))


def test_at_put_answers_the_receiver_for_chaining() -> None:
    # As `Dict.at_put` and `ByteArray.at_put` do: a POOP-specific message with
    # no Python counterpart to mirror.
    xs = List(Int(1))
    assert xs.at_put(Int(0), Int(5)) is xs


def test_at_put_counts_from_the_end_like_at() -> None:
    xs = List(Int(1), Int(2))
    xs.at_put(Int(-1), Int(9))
    assert xs == List(Int(1), Int(9))


def test_at_put_out_of_range_answers_the_same_sentence_as_at() -> None:
    with pytest.raises(IndexError, match="list has no element at 9 — it has 2"):
        List(Int(1), Int(2)).at_put(Int(9), Int(0))


def test_at_put_refuses_an_index_that_is_not_one() -> None:
    # `list indices must be integers or slices, not str` names the
    # subscripting this message replaces.
    with pytest.raises(
        TypeError, match=r"^list.at_put expects an int index, got a str$"
    ):
        List(Int(1)).at_put(Str("a"), Int(0))  # ty: ignore[invalid-argument-type]
