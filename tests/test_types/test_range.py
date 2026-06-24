import pytest

from poop.types.boolean import Boolean, false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.range import Range
from poop.types.string import Str


def _range(start: int, stop: int) -> Range:
    return Range(Int(start), Int(stop))


def test_str() -> None:
    assert str(_range(1, 3)) == "range(1, 3)"


def test_str_with_step() -> None:
    assert str(Range(Int(1), Int(9), Int(2))) == "range(1, 9, 2)"


def test_str_descending() -> None:
    assert str(_range(5, 3)) == "range(5, 3, -1)"


def test_repr_delegates_to_str() -> None:
    r = _range(1, 3)
    assert repr(r) == str(r)


def test_len() -> None:
    assert _range(1, 3).len() == Int(3)
    assert _range(1, 1).len() == Int(1)


def test_do_iterates_all_elements() -> None:
    results: list[int] = []
    _range(1, 3).do(lambda i: results.append(int(i)))
    assert results == [1, 2, 3]


def test_do_descending_range() -> None:
    results: list[int] = []
    _range(5, 3).do(lambda i: results.append(int(i)))
    assert results == [5, 4, 3]


def test_map_transforms_elements() -> None:
    result = _range(1, 3).map(lambda i: i + Int(10))
    assert List(*result) == List(Int(11), Int(12), Int(13))


def test_filter_keeps_matching() -> None:
    result = _range(1, 5).filter(lambda i: i % Int(2) == Int(0))
    assert List(*result) == List(Int(2), Int(4))


def test_filter_false_keeps_non_matching() -> None:
    result = _range(1, 5).filter_false(lambda i: i % Int(2) == Int(0))
    assert List(*result) == List(Int(1), Int(3), Int(5))


def test_detect_finds_first_match() -> None:
    result = _range(1, 5).find(lambda i: i > Int(3))
    assert result == Int(4)


def test_detect_returns_none_when_not_found() -> None:
    assert _range(1, 5).find(lambda i: i > Int(9)) is none


def test_do_returns_none() -> None:
    assert _range(1, 3).do(lambda i: i) is none


def test_reduce_sum() -> None:
    assert _range(1, 5).reduce(Int(0), lambda acc, i: acc + i) == Int(15)


def test_reduce_product() -> None:
    assert _range(1, 4).reduce(Int(1), lambda acc, i: acc * i) == Int(24)


def test_is_none_inherited() -> None:
    assert _range(1, 3).is_none() is false


def test_class_name() -> None:
    assert _range(1, 3).class_name() == Str("range")


def test_equal_ranges_compare_equal() -> None:
    # Two ranges with the same sequence must compare equal (mirroring
    # Python's `range`), and the result must be a POOP Boolean — not a
    # raw Python bool — so transparency holds.
    result = _range(0, 5) == _range(0, 5)
    assert isinstance(result, Boolean)
    assert result is true


def test_unequal_ranges_compare_unequal() -> None:
    assert (_range(0, 5) == _range(0, 7)) is false
    assert (_range(0, 5) != _range(0, 7)) is true


def test_ranges_with_same_sequence_but_different_encoding_are_equal() -> None:
    # Range(0, 4, 2) and Range(0, 5, 2) both yield [0, 2, 4]; POOP's
    # inclusive upper bound is an internal detail and must not leak into
    # equality.
    a = Range(Int(0), Int(4), Int(2))
    b = Range(Int(0), Int(5), Int(2))
    assert (a == b) is true


def test_range_not_equal_to_non_range() -> None:
    assert (_range(0, 5) == Int(0)) is false


def test_equal_ranges_hash_equal() -> None:
    assert hash(_range(0, 5)) == hash(_range(0, 5))
    assert {_range(0, 5): Int(1)}[_range(0, 5)] == Int(1)


def test_all_returns_true_when_all_match() -> None:
    assert _range(2, 4).all(lambda i: i > Int(1)) is true


def test_all_returns_false_when_some_dont_match() -> None:
    assert _range(1, 4).all(lambda i: i > Int(2)) is false


def test_any_returns_true_when_some_match() -> None:
    assert _range(1, 4).any(lambda i: i > Int(3)) is true


def test_any_returns_false_when_none_match() -> None:
    assert _range(1, 3).any(lambda i: i > Int(5)) is false


def test_includes_returns_true_for_element_in_range() -> None:
    assert _range(1, 5).includes(Int(3)) is true


def test_includes_returns_false_for_element_outside_range() -> None:
    assert _range(1, 5).includes(Int(6)) is false


def test_at_returns_element() -> None:
    assert _range(3, 7).at(Int(0)) == Int(3)


def test_at_negative_index() -> None:
    assert _range(3, 7).at(Int(-1)) == Int(7)


def test_reversed_iterates_in_reverse() -> None:
    results: list[int] = []
    _range(1, 3).reversed().do(lambda i: results.append(int(i)))
    assert results == [3, 2, 1]


def test_reversed_len_is_same() -> None:
    assert _range(1, 5).reversed().len() == Int(5)


def test_range_with_ascending_step() -> None:
    results: list[int] = []
    Range(Int(1), Int(9), Int(2)).do(lambda i: results.append(int(i)))
    assert results == [1, 3, 5, 7, 9]


def test_range_with_descending_step() -> None:
    results: list[int] = []
    Range(Int(9), Int(1), Int(-2)).do(lambda i: results.append(int(i)))
    assert results == [9, 7, 5, 3, 1]


def test_range_with_step_len() -> None:
    assert Range(Int(1), Int(9), Int(2)).len() == Int(5)


def test_reversed_with_step() -> None:
    results: list[int] = []
    Range(Int(1), Int(9), Int(2)).reversed().do(lambda i: results.append(int(i)))
    assert results == [9, 7, 5, 3, 1]


# Regression: when stop is not on a step boundary, the forward sequence's last
# element is not stop, so seeding the reversed range from stop produced
# non-members. reversed() must mirror CPython's reversed(range(...)).
def test_reversed_with_step_off_boundary() -> None:
    results: list[int] = []
    Range(Int(0), Int(10), Int(3)).reversed().do(lambda i: results.append(int(i)))
    assert results == [9, 6, 3, 0]
    assert results == list(reversed(range(0, 11, 3)))


def test_reversed_descending_off_boundary() -> None:
    results: list[int] = []
    Range(Int(10), Int(0), Int(-3)).reversed().do(lambda i: results.append(int(i)))
    assert results == [1, 4, 7, 10]
    assert results == list(reversed(range(10, -1, -3)))


def test_reversed_single_element() -> None:
    results: list[int] = []
    Range(Int(5), Int(5), Int(1)).reversed().do(lambda i: results.append(int(i)))
    assert results == [5]


def test_reversed_empty_stays_empty() -> None:
    empty = Range(Int(5), Int(3), Int(1))
    assert empty.len() == Int(0)
    results: list[int] = []
    empty.reversed().do(lambda i: results.append(int(i)))
    assert results == []
    assert empty.reversed().len() == Int(0)


def test_start() -> None:
    assert _range(3, 7).start == Int(3)


def test_stop() -> None:
    assert _range(3, 7).stop == Int(7)


def test_step_default_ascending() -> None:
    assert _range(1, 5).step == Int(1)


def test_step_default_descending() -> None:
    assert _range(5, 1).step == Int(-1)


def test_step_explicit() -> None:
    assert Range(Int(1), Int(9), Int(2)).step == Int(2)


def test_count_present() -> None:
    assert _range(1, 5).count(Int(3)) == Int(1)


def test_count_absent() -> None:
    assert _range(1, 5).count(Int(9)) == Int(0)


def test_count_with_step_not_hit() -> None:
    assert Range(Int(1), Int(9), Int(2)).count(Int(4)) == Int(0)


def test_index_found() -> None:
    assert _range(1, 5).index(Int(3)) == Int(2)


def test_index_first_element() -> None:
    assert _range(1, 5).index(Int(1)) == Int(0)


def test_index_not_found_raises() -> None:
    with pytest.raises(ValueError):
        _range(1, 5).index(Int(9))


def test_slice_with_step() -> None:
    result = _range(0, 10).slice(Int(0), Int(5), Int(2))
    assert result == List(Int(0), Int(2), Int(4))


def test_slice_open_ended() -> None:
    # proposal 143: open-ended slice with a POOP `none` stop. POOP's Range
    # is inclusive, so range(0, 5) is [0, 1, 2, 3, 4, 5].
    assert _range(0, 5).slice(Int(2), none) == List(Int(2), Int(3), Int(4), Int(5))


def test_sum_returns_total() -> None:
    assert _range(1, 4).sum() == Int(10)


def test_sum_single_element() -> None:
    assert _range(5, 5).sum() == Int(5)


def test_step_zero_raises_at_construction() -> None:
    with pytest.raises(ValueError, match="step must not be zero"):
        Range(Int(0), Int(5), Int(0))
