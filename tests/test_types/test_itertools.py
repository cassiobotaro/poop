from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- pairwise ---


def test_pairwise_yields_adjacent_tuples() -> None:
    pairs = list(List(Int(1), Int(2), Int(3)).pairwise())
    assert pairs == [Tuple(Int(1), Int(2)), Tuple(Int(2), Int(3))]


def test_pairwise_on_short_iterable_is_empty() -> None:
    assert list(List(Int(1)).pairwise()) == []


# --- batched ---


def test_batched_groups_into_tuples() -> None:
    batches = list(List(Int(1), Int(2), Int(3)).batched(Int(2)))
    assert batches == [Tuple(Int(1), Int(2)), Tuple(Int(3))]


def test_batched_exact_division() -> None:
    batches = list(List(Int(1), Int(2)).batched(Int(2)))
    assert batches == [Tuple(Int(1), Int(2))]


# --- chain ---


def test_chain_concatenates_iterables() -> None:
    chained = list(List(Int(1)).chain(List(Int(2)), List(Int(3))))
    assert chained == [Int(1), Int(2), Int(3)]


def test_chain_alone_yields_self_items() -> None:
    assert list(List(Int(1), Int(2)).chain()) == [Int(1), Int(2)]


# --- accumulate ---


def test_accumulate_defaults_to_running_sum() -> None:
    totals = list(List(Int(1), Int(2), Int(3)).accumulate())
    assert totals == [Int(1), Int(3), Int(6)]


def test_accumulate_with_block() -> None:
    totals = list(List(Int(2), Int(3), Int(4)).accumulate(lambda a, b: a * b))
    assert totals == [Int(2), Int(6), Int(24)]


def test_accumulate_concatenates_strings() -> None:
    parts = list(List(Str("a"), Str("b")).accumulate())
    assert parts == [Str("a"), Str("ab")]


# --- product ---


def test_product_yields_cartesian_tuples() -> None:
    combos = list(List(Int(1), Int(2)).product(List(Str("a"))))
    assert combos == [Tuple(Int(1), Str("a")), Tuple(Int(2), Str("a"))]


def test_product_alone_wraps_items() -> None:
    assert list(List(Int(1)).product()) == [Tuple(Int(1))]


# --- combinations ---


def test_combinations_yields_sorted_subsets() -> None:
    combos = list(List(Int(1), Int(2), Int(3)).combinations(Int(2)))
    assert combos == [
        Tuple(Int(1), Int(2)),
        Tuple(Int(1), Int(3)),
        Tuple(Int(2), Int(3)),
    ]


# --- permutations ---


def test_permutations_full_length_by_default() -> None:
    perms = list(List(Int(1), Int(2)).permutations())
    assert perms == [Tuple(Int(1), Int(2)), Tuple(Int(2), Int(1))]


def test_permutations_with_length() -> None:
    perms = list(List(Int(1), Int(2), Int(3)).permutations(Int(1)))
    assert perms == [Tuple(Int(1)), Tuple(Int(2)), Tuple(Int(3))]


# --- combinator shape ---


def test_combinators_are_lazy_one_shot() -> None:
    pairs = List(Int(1), Int(2), Int(3)).pairwise()
    assert pairs.next() == Tuple(Int(1), Int(2))
    assert list(pairs) == [Tuple(Int(2), Int(3))]


def test_combinators_compose_with_map_and_filter() -> None:
    sums = list(
        List(Int(1), Int(2), Int(3))
        .pairwise()
        .map(lambda pair: pair.at(Int(0)) + pair.at(Int(1)))
    )
    assert sums == [Int(3), Int(5)]


def test_combinators_chain_into_each_other() -> None:
    result = list(List(Int(1), Int(2)).chain(List(Int(3))).pairwise())
    assert result == [Tuple(Int(1), Int(2)), Tuple(Int(2), Int(3))]


def test_combinator_eq_is_identity() -> None:
    p = List(Int(1), Int(2)).pairwise()
    assert (p == p) is true
    assert (p == List(Int(1), Int(2)).pairwise()) is false


def test_combinator_masquerades_python_name() -> None:
    p = List(Int(1), Int(2)).pairwise()
    assert type(p).__name__ == "pairwise"
    assert str(p) == "<pairwise>"


def test_combinators_work_on_tuple() -> None:
    pairs = list(Tuple(Str("a"), Str("b"), Str("c")).pairwise())
    assert pairs == [Tuple(Str("a"), Str("b")), Tuple(Str("b"), Str("c"))]


# --- Interpreter integration ---


def test_pairwise_via_interpreter() -> None:
    Interpreter().run_source("[1, 2, 3].pairwise().do(lambda pair: pair.print())")


def test_accumulate_via_interpreter() -> None:
    Interpreter().run_source("[1, 2, 3].accumulate().do(lambda total: total.print())")


def test_combinations_via_interpreter() -> None:
    Interpreter().run_source("[1, 2, 3].combinations(2).do(lambda pair: pair.print())")
