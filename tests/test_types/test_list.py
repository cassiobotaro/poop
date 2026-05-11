import pytest

from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none


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


def test_index_not_found_raises() -> None:
    with pytest.raises(ValueError):
        List(Int(1), Int(2)).index(Int(9))


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
    lst.sort(reverse=True)
    assert lst == List(Int(3), Int(2), Int(1))


def test_slice_with_step() -> None:
    assert List(Int(0), Int(1), Int(2), Int(3), Int(4)).slice(
        Int(0), Int(5), Int(2)
    ) == List(Int(0), Int(2), Int(4))


def test_add_concatenates() -> None:
    assert List(Int(1), Int(2)) + List(Int(3), Int(4)) == List(
        Int(1), Int(2), Int(3), Int(4)
    )


def test_mul_repeats() -> None:
    assert List(Int(1), Int(2)) * Int(2) == List(Int(1), Int(2), Int(1), Int(2))


def test_eq_with_non_list_returns_false() -> None:
    assert List(Int(1)).__eq__(Int(1)) is false


def test_ne_with_non_list_returns_true() -> None:
    assert List(Int(1)).__ne__(Int(1)) is true


def test_print_accepts_poop_none_kwargs(capsys: pytest.CaptureFixture[str]) -> None:
    List(Int(1), Int(2)).print(sep=none, end=none, flush=none)
    captured = capsys.readouterr()
    assert captured.out == "1 2\n"
