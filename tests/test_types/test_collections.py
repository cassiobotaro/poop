import pytest

from poop.types.boolean import false, true
from poop.types.collections import Counter, Deque
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- Counter ---


def test_counter_constructs_empty() -> None:
    assert isinstance(Counter(), Counter)
    assert Counter().len() == Int(0)


def test_counter_constructs_from_none() -> None:
    assert Counter(none).len() == Int(0)


def test_counter_counts_str_characters() -> None:
    c = Counter(Str("aabbb"))
    assert c.at(Str("a")) == Int(2)
    assert c.at(Str("b")) == Int(3)


def test_counter_counts_list_elements() -> None:
    c = Counter(List(Int(1), Int(1), Int(2)))
    assert c.at(Int(1)) == Int(2)
    assert c.at(Int(2)) == Int(1)


def test_counter_constructs_from_dict_of_counts() -> None:
    d = Dict()
    d.at_put(Str("x"), Int(4))
    c = Counter(d)
    assert c.at(Str("x")) == Int(4)


def test_counter_constructs_from_counter() -> None:
    a = Counter(Str("aa"))
    b = Counter(a)
    assert b.at(Str("a")) == Int(2)
    assert (a == b) is true


def test_counter_missing_key_answers_zero() -> None:
    assert Counter().at(Str("ghost")) == Int(0)


def test_counter_at_put_sets_count_and_returns_self() -> None:
    c = Counter()
    assert c.at_put(Str("a"), Int(7)) is c
    assert c.at(Str("a")) == Int(7)


def test_counter_most_common_orders_by_count() -> None:
    pairs = Counter(Str("aabbb")).most_common()
    assert pairs == List(Tuple(Str("b"), Int(3)), Tuple(Str("a"), Int(2)))


def test_counter_most_common_limits_to_n() -> None:
    pairs = Counter(Str("aabbbc")).most_common(Int(1))
    assert pairs == List(Tuple(Str("b"), Int(3)))


def test_counter_elements_repeats_by_count() -> None:
    elements = Counter(Str("aab")).elements()
    assert elements == List(Str("a"), Str("a"), Str("b"))


def test_counter_total_sums_counts() -> None:
    assert Counter(Str("aabbb")).total() == Int(5)


def test_counter_update_adds_counts() -> None:
    c = Counter(Str("a"))
    assert c.update(Str("ab")) is none
    assert c.at(Str("a")) == Int(2)
    assert c.at(Str("b")) == Int(1)


def test_counter_update_with_none_is_noop() -> None:
    c = Counter(Str("a"))
    assert c.update(none) is none
    assert c.total() == Int(1)


def test_counter_subtract_decrements_counts() -> None:
    c = Counter(Str("aab"))
    assert c.subtract(Str("ab")) is none
    assert c.at(Str("a")) == Int(1)
    assert c.at(Str("b")) == Int(0)


def test_counter_len_counts_distinct_elements() -> None:
    c = Counter(Str("aabbb"))
    assert c.len() == Int(2)
    assert len(c) == 2


def test_counter_includes() -> None:
    c = Counter(Str("a"))
    assert c.includes(Str("a")) is true
    assert c.includes(Str("z")) is false
    assert Str("a") in c


def test_counter_do_iterates_element_count_pairs() -> None:
    seen = []
    Counter(Str("aab")).do(lambda pair: seen.append(pair))
    assert Tuple(Str("a"), Int(2)) in seen
    assert Tuple(Str("b"), Int(1)) in seen


def test_counter_iterates_distinct_elements() -> None:
    assert sorted(s._value for s in Counter(Str("aab"))) == ["a", "b"]


def test_counter_add_merges_counts() -> None:
    c = Counter(Str("aa")) + Counter(Str("ab"))
    assert isinstance(c, Counter)
    assert c.at(Str("a")) == Int(3)
    assert c.at(Str("b")) == Int(1)


def test_counter_sub_keeps_positive_counts() -> None:
    c = Counter(Str("aab")) - Counter(Str("ab"))
    assert c.at(Str("a")) == Int(1)
    assert c.at(Str("b")) == Int(0)


def test_counter_and_takes_minimum() -> None:
    c = Counter(Str("aab")) & Counter(Str("abb"))
    assert c.at(Str("a")) == Int(1)
    assert c.at(Str("b")) == Int(1)


def test_counter_or_takes_maximum() -> None:
    c = Counter(Str("aab")) | Counter(Str("abb"))
    assert c.at(Str("a")) == Int(2)
    assert c.at(Str("b")) == Int(2)


def test_counter_arithmetic_rejects_non_counter() -> None:
    try:
        Counter() + Int(1)
        raised = False
    except TypeError:
        raised = True
    assert raised


def test_counter_eq_compares_counts() -> None:
    assert (Counter(Str("ab")) == Counter(Str("ba"))) is true
    assert (Counter(Str("a")) == Counter(Str("b"))) is false
    assert (Counter(Str("a")) != Counter(Str("b"))) is true
    assert (Counter() == Int(0)) is false


def test_counter_str_masquerades_as_python_counter() -> None:
    assert str(Counter(Str("aa"))) == "Counter({'a': 2})"


# --- Deque ---


def test_deque_constructs_empty() -> None:
    assert isinstance(Deque(), Deque)
    assert Deque().len() == Int(0)


def test_deque_constructs_from_iterable() -> None:
    d = Deque(List(Int(1), Int(2)))
    assert d.len() == Int(2)
    assert d.at(Int(0)) == Int(1)


def test_deque_constructs_from_none() -> None:
    assert Deque(none).len() == Int(0)


def test_deque_maxlen_discards_from_opposite_end() -> None:
    d = Deque(List(Int(1), Int(2), Int(3)), maxlen=Int(2))
    assert d.len() == Int(2)
    assert d.at(Int(0)) == Int(2)


def test_deque_maxlen_property() -> None:
    assert Deque(maxlen=Int(5)).maxlen == Int(5)
    assert Deque().maxlen is none


def test_deque_append_and_pop() -> None:
    d = Deque()
    assert d.append(Int(1)) is none
    d.append(Int(2))
    assert d.pop() == Int(2)
    assert d.len() == Int(1)


def test_deque_appendleft_and_popleft() -> None:
    d = Deque(List(Int(2)))
    assert d.appendleft(Int(1)) is none
    assert d.popleft() == Int(1)
    assert d.popleft() == Int(2)


def test_deque_pop_empty_raises() -> None:
    with pytest.raises(IndexError):
        Deque().pop()


def test_deque_extend_appends_right() -> None:
    d = Deque(List(Int(1)))
    assert d.extend(List(Int(2), Int(3))) is none
    assert d.at(Int(2)) == Int(3)


def test_deque_extendleft_reverses_order() -> None:
    d = Deque(List(Int(3)))
    assert d.extendleft(List(Int(2), Int(1))) is none
    assert d.at(Int(0)) == Int(1)


def test_deque_rotate_defaults_to_one() -> None:
    d = Deque(List(Int(1), Int(2), Int(3)))
    assert d.rotate() is none
    assert d.at(Int(0)) == Int(3)


def test_deque_rotate_negative_rotates_left() -> None:
    d = Deque(List(Int(1), Int(2), Int(3)))
    d.rotate(Int(-1))
    assert d.at(Int(0)) == Int(2)


def test_deque_clear_empties() -> None:
    d = Deque(List(Int(1)))
    assert d.clear() is none
    assert d.len() == Int(0)


def test_deque_count() -> None:
    d = Deque(List(Int(1), Int(1), Int(2)))
    assert d.count(Int(1)) == Int(2)


def test_deque_remove_first_occurrence() -> None:
    d = Deque(List(Int(1), Int(2), Int(1)))
    assert d.remove(Int(1)) is none
    assert d.len() == Int(2)
    assert d.at(Int(0)) == Int(2)


def test_deque_reverse() -> None:
    d = Deque(List(Int(1), Int(2)))
    assert d.reverse() is none
    assert d.at(Int(0)) == Int(2)


def test_deque_at_supports_negative_index() -> None:
    d = Deque(List(Int(1), Int(2)))
    assert d.at(Int(-1)) == Int(2)


def test_deque_includes() -> None:
    d = Deque(List(Int(1)))
    assert d.includes(Int(1)) is true
    assert d.includes(Int(9)) is false
    assert Int(1) in d


def test_deque_do_iterates_items() -> None:
    seen = []
    Deque(List(Int(1), Int(2))).do(lambda x: seen.append(x))
    assert seen == [Int(1), Int(2)]


def test_deque_map_and_filter_via_iterable_mixin() -> None:
    d = Deque(List(Int(1), Int(2), Int(3)))
    doubled = [x for x in d.map(lambda x: x + Int(1))]
    assert doubled == [Int(2), Int(3), Int(4)]
    odd = [x for x in d.filter(lambda x: bool(x % Int(2)))]
    assert odd == [Int(1), Int(3)]


def test_deque_eq_compares_contents() -> None:
    assert (Deque(List(Int(1))) == Deque(List(Int(1)))) is true
    assert (Deque(List(Int(1))) == Deque(List(Int(2)))) is false
    assert (Deque() == Int(0)) is false


def test_deque_str_masquerades_as_python_deque() -> None:
    assert str(Deque(List(Int(1)))) == "deque([1])"
