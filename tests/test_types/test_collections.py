from poop.types.boolean import false, true
from poop.types.collections import Counter
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
