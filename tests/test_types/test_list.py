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


def test_getitem() -> None:
    lst = List(Int(10), Int(20))
    assert lst[Int(1)] == Int(20)


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
    List(Int(1), Int(2), Int(3)).for_each(lambda x: results.append(x))
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
