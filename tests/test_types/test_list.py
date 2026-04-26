import pytest

from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.list import List


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


def test_add_returns_self() -> None:
    lst = List(Int(1))
    result = lst.add(Int(2))
    assert result is lst
    assert lst.len() == Int(2)


def test_add_appends() -> None:
    lst = List()
    lst.add(Int(1)).add(Int(2)).add(Int(3))
    assert lst == List(Int(1), Int(2), Int(3))


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


def test_collect_maps() -> None:
    result = List(Int(1), Int(2), Int(3)).map(lambda x: x + Int(10))
    assert result == List(Int(11), Int(12), Int(13))


def test_collect_returns_list() -> None:
    assert isinstance(List(Int(1)).map(lambda x: x), List)


def test_select_filters() -> None:
    result = List(Int(1), Int(2), Int(3), Int(4)).filter(lambda x: x % Int(2) == Int(0))
    assert result == List(Int(2), Int(4))


def test_reject_filters_inverse() -> None:
    result = List(Int(1), Int(2), Int(3), Int(4)).filter_false(
        lambda x: x % Int(2) == Int(0)
    )
    assert result == List(Int(1), Int(3))


def test_detect_finds_first() -> None:
    result = List(Int(1), Int(2), Int(3)).find(lambda x: x > Int(1))
    assert result == Int(2)


def test_detect_returns_none_when_not_found() -> None:
    from poop.types.none import none

    result = List(Int(1), Int(2)).find(lambda x: x > Int(10))
    assert result is none


def test_inject_into_reduces() -> None:
    result = List(Int(1), Int(2), Int(3), Int(4)).reduce(Int(0), lambda acc, x: acc + x)
    assert result == Int(10)


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


def test_first() -> None:
    assert List(Int(10), Int(20), Int(30)).first() == Int(10)


def test_last() -> None:
    assert List(Int(10), Int(20), Int(30)).last() == Int(30)


def test_pop_returns_last_element() -> None:
    lst = List(Int(10), Int(20), Int(30))
    assert lst.pop() == Int(30)


def test_pop_removes_last_element() -> None:
    lst = List(Int(10), Int(20), Int(30))
    lst.pop()
    assert lst.len() == Int(2)
    assert lst.last() == Int(20)


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
    from poop.types.int import Int

    lst = List(Int(-3), Int(1), Int(-2))
    result = lst.sorted(key=lambda x: x.abs())
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


def test_clear_returns_self() -> None:
    lst = List(Int(1))
    assert lst.clear() is lst


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


def test_extend_returns_self() -> None:
    lst = List(Int(1))
    assert lst.extend(List(Int(2))) is lst


def test_index_found() -> None:
    assert List(Int(10), Int(20), Int(30)).index(Int(20)) == Int(1)


def test_index_not_found_raises() -> None:
    import pytest

    with pytest.raises(ValueError):
        List(Int(1), Int(2)).index(Int(9))


def test_insert_at_position() -> None:
    lst = List(Int(1), Int(3))
    lst.insert(Int(1), Int(2))
    assert lst == List(Int(1), Int(2), Int(3))


def test_insert_returns_self() -> None:
    lst = List(Int(1))
    assert lst.insert(Int(0), Int(0)) is lst


def test_remove_first_occurrence() -> None:
    lst = List(Int(1), Int(2), Int(1))
    lst.remove(Int(1))
    assert lst == List(Int(2), Int(1))


def test_remove_returns_self() -> None:
    lst = List(Int(1))
    assert lst.remove(Int(1)) is lst


def test_remove_not_found_raises() -> None:
    import pytest

    with pytest.raises(ValueError):
        List(Int(1)).remove(Int(9))


def test_reverse_mutates_in_place() -> None:
    lst = List(Int(1), Int(2), Int(3))
    lst.reverse()
    assert lst == List(Int(3), Int(2), Int(1))


def test_reverse_returns_self() -> None:
    lst = List(Int(1), Int(2))
    assert lst.reverse() is lst


def test_sort_mutates_in_place() -> None:
    lst = List(Int(3), Int(1), Int(2))
    lst.sort()
    assert lst == List(Int(1), Int(2), Int(3))


def test_sort_returns_self() -> None:
    lst = List(Int(3), Int(1))
    assert lst.sort() is lst


def test_sort_with_key() -> None:
    lst = List(Int(-3), Int(1), Int(-2))
    lst.sort(key=lambda x: x.abs())
    assert lst == List(Int(1), Int(-2), Int(-3))


def test_sort_reverse() -> None:
    lst = List(Int(1), Int(2), Int(3))
    lst.sort(reverse=True)
    assert lst == List(Int(3), Int(2), Int(1))


def test_copy_from_to_with_step() -> None:
    assert List(Int(0), Int(1), Int(2), Int(3), Int(4)).copy_from_to(
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
