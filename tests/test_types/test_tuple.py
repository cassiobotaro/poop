from poop.types.boolean import false, true
from poop.types.int import Int
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


def test_getitem() -> None:
    t = Tuple(Int(10), Int(20))
    assert t[Int(1)] == Int(20)


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


def test_collect_maps() -> None:
    result = Tuple(Int(1), Int(2), Int(3)).map(lambda x: x + Int(10))
    assert result == Tuple(Int(11), Int(12), Int(13))


def test_collect_returns_tuple() -> None:
    assert isinstance(Tuple(Int(1)).map(lambda x: x), Tuple)


def test_select_filters() -> None:
    result = Tuple(Int(1), Int(2), Int(3), Int(4)).filter(
        lambda x: x % Int(2) == Int(0)
    )
    assert result == Tuple(Int(2), Int(4))


def test_reject_filters_inverse() -> None:
    result = Tuple(Int(1), Int(2), Int(3), Int(4)).filter_false(
        lambda x: x % Int(2) == Int(0)
    )
    assert result == Tuple(Int(1), Int(3))


def test_detect_finds_first() -> None:
    result = Tuple(Int(1), Int(2), Int(3)).find(lambda x: x > Int(1))
    assert result == Int(2)


def test_detect_returns_none_when_not_found() -> None:
    from poop.types.none import none

    result = Tuple(Int(1), Int(2)).find(lambda x: x > Int(10))
    assert result is none


def test_inject_into_reduces() -> None:
    result = Tuple(Int(1), Int(2), Int(3), Int(4)).reduce(
        Int(0), lambda acc, x: acc + x
    )
    assert result == Int(10)


def test_all_true() -> None:
    assert Tuple(Int(2), Int(4), Int(6)).all(lambda x: x % Int(2) == Int(0)) is true


def test_all_false() -> None:
    assert Tuple(Int(1), Int(2), Int(3)).all(lambda x: x % Int(2) == Int(0)) is false


def test_any_true() -> None:
    assert Tuple(Int(1), Int(2), Int(3)).any(lambda x: x % Int(2) == Int(0)) is true


def test_any_false() -> None:
    assert Tuple(Int(1), Int(3)).any(lambda x: x % Int(2) == Int(0)) is false


def test_first() -> None:
    assert Tuple(Int(10), Int(20), Int(30)).first() == Int(10)


def test_last() -> None:
    assert Tuple(Int(10), Int(20), Int(30)).last() == Int(30)


def test_iter() -> None:
    items = list(Tuple(Int(1), Int(2), Int(3)))
    assert items == [Int(1), Int(2), Int(3)]


def test_eq_equal_tuples() -> None:
    assert Tuple(Int(1), Int(2)) == Tuple(Int(1), Int(2))


def test_eq_different_tuples() -> None:
    assert (Tuple(Int(1), Int(2)) == Tuple(Int(1), Int(3))) is false


def test_ne_different_tuples() -> None:
    assert (Tuple(Int(1)) != Tuple(Int(2))) is true


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
    from poop.types.list import List

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
    result = t.sorted(key=lambda x: x.abs())
    assert result == Tuple(Int(1), Int(-2), Int(-3))


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
    import pytest

    with pytest.raises(ValueError):
        Tuple(Int(1), Int(2)).index(Int(9))


def test_copy_from_to_with_step() -> None:
    t = Tuple(Int(0), Int(1), Int(2), Int(3), Int(4))
    assert t.copy_from_to(Int(0), Int(5), Int(2)) == Tuple(Int(0), Int(2), Int(4))


def test_add_concatenates() -> None:
    assert Tuple(Int(1), Int(2)) + Tuple(Int(3), Int(4)) == Tuple(Int(1), Int(2), Int(3), Int(4))


def test_mul_repeats() -> None:
    assert Tuple(Int(1), Int(2)) * Int(2) == Tuple(Int(1), Int(2), Int(1), Int(2))


def test_ne_with_non_tuple_returns_true() -> None:
    from poop.types.list import List

    assert Tuple(Int(1)).__ne__(List(Int(1))) is true
