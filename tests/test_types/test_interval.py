from poop.types.int import Int
from poop.types.interval import Interval


def _interval(start: int, stop: int) -> Interval:
    return Interval(Int(start), Int(stop))


def test_str() -> None:
    assert str(_interval(1, 3)) == "(1..3)"


def test_repr_delegates_to_str() -> None:
    iv = _interval(1, 3)
    assert repr(iv) == str(iv)


def test_len() -> None:
    assert _interval(1, 3).len() == Int(3)
    assert _interval(1, 1).len() == Int(1)


def test_do_iterates_all_elements() -> None:
    results: list[int] = []
    _interval(1, 3).for_each(lambda i: results.append(int(i)))
    assert results == [1, 2, 3]


def test_do_descending_interval() -> None:
    results: list[int] = []
    _interval(5, 3).for_each(lambda i: results.append(int(i)))
    assert results == [5, 4, 3]


def test_collect_transforms_elements() -> None:
    from poop.types.list import List

    result = _interval(1, 3).map(lambda i: i + Int(10))
    assert result == List(Int(11), Int(12), Int(13))


def test_select_filters_elements() -> None:
    from poop.types.list import List

    result = _interval(1, 5).filter(lambda i: i % Int(2) == Int(0))
    assert result == List(Int(2), Int(4))


def test_reject_filters_elements() -> None:
    from poop.types.list import List

    result = _interval(1, 5).filter_false(lambda i: i % Int(2) == Int(0))
    assert result == List(Int(1), Int(3), Int(5))


def test_detect_finds_first_match() -> None:
    result = _interval(1, 5).find(lambda i: i > Int(3))
    assert result == Int(4)


def test_detect_returns_none_when_not_found() -> None:
    from poop.types.none import none

    assert _interval(1, 5).find(lambda i: i > Int(9)) is none


def test_inject_into_sums() -> None:
    result = _interval(1, 5).reduce(Int(0), lambda acc, i: acc + i)
    assert result == Int(15)


def test_inject_into_product() -> None:
    result = _interval(1, 4).reduce(Int(1), lambda acc, i: acc * i)
    assert result == Int(24)


def test_is_none_inherited() -> None:
    from poop.types.boolean import false

    assert _interval(1, 3).is_none() is false


def test_class_name() -> None:
    from poop.types.string import Str

    assert _interval(1, 3).class_name() == Str("Interval")


def test_all_returns_true_when_all_match() -> None:
    from poop.types.boolean import true

    assert _interval(2, 4).all(lambda i: i > Int(1)) is true


def test_all_returns_false_when_some_dont_match() -> None:
    from poop.types.boolean import false

    assert _interval(1, 4).all(lambda i: i > Int(2)) is false


def test_any_returns_true_when_some_match() -> None:
    from poop.types.boolean import true

    assert _interval(1, 4).any(lambda i: i > Int(3)) is true


def test_any_returns_false_when_none_match() -> None:
    from poop.types.boolean import false

    assert _interval(1, 3).any(lambda i: i > Int(5)) is false


def test_includes_returns_true_for_element_in_range() -> None:
    from poop.types.boolean import true

    assert _interval(1, 5).includes(Int(3)) is true


def test_includes_returns_false_for_element_outside_range() -> None:
    from poop.types.boolean import false

    assert _interval(1, 5).includes(Int(6)) is false


def test_first_returns_start() -> None:
    assert _interval(3, 7).first() == Int(3)


def test_last_returns_stop() -> None:
    assert _interval(3, 7).last() == Int(7)


def test_reversed_iterates_in_reverse() -> None:
    results: list[int] = []
    _interval(1, 3).reversed().for_each(lambda i: results.append(int(i)))
    assert results == [3, 2, 1]


def test_reversed_len_is_same() -> None:
    assert _interval(1, 5).reversed().len() == Int(5)


def test_to_by_ascending_step() -> None:
    results: list[int] = []
    Int(1).to_by_(Int(9), Int(2)).for_each(lambda i: results.append(int(i)))
    assert results == [1, 3, 5, 7, 9]


def test_to_by_descending_step() -> None:
    results: list[int] = []
    Int(9).to_by_(Int(1), Int(-2)).for_each(lambda i: results.append(int(i)))
    assert results == [9, 7, 5, 3, 1]


def test_to_by_len() -> None:
    assert Int(1).to_by_(Int(9), Int(2)).len() == Int(5)


def test_reversed_with_step() -> None:
    results: list[int] = []
    Int(1).to_by_(Int(9), Int(2)).reversed().for_each(lambda i: results.append(int(i)))
    assert results == [9, 7, 5, 3, 1]
