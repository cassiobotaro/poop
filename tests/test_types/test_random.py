from typing import cast

from poop.interpreter import Interpreter
from poop.types.float import Float
from poop.types.int import Int
from poop.types.random import _DEFAULT, Random


def test_random_returns_poop_float_in_unit_range() -> None:
    result = _DEFAULT.random()
    assert isinstance(result, Float)
    assert 0.0 <= result._value < 1.0


def test_new_returns_fresh_instance() -> None:
    fresh = _DEFAULT.new(Int(42))
    assert isinstance(fresh, Random)
    assert fresh is not _DEFAULT


def test_same_seed_yields_same_sequence() -> None:
    a = Random(Int(42))
    b = Random(Int(42))
    assert a.random()._value == b.random()._value
    assert a.random()._value == b.random()._value


def test_random_reachable_via_interpreter() -> None:
    Interpreter().run_source("Random.random().print()")


# --- Bookkeeping ---


def test_seed_makes_sequence_deterministic() -> None:
    r = Random()
    r.seed(Int(42))
    first = r.random()._value
    r.seed(Int(42))
    second = r.random()._value
    assert first == second


def test_seed_returns_none_singleton() -> None:
    from poop.types.none import none

    r = Random()
    assert r.seed(Int(1)) is none


# --- Core draws ---


def test_uniform_returns_float_in_range() -> None:
    r = Random(Int(0))
    result = r.uniform(Float(1.0), Float(2.0))
    assert isinstance(result, Float)
    assert 1.0 <= result._value <= 2.0


def test_randint_inclusive_both_ends() -> None:
    r = Random(Int(0))
    result = r.randint(Int(5), Int(5))
    assert isinstance(result, Int)
    assert result._value == 5


def test_randint_within_range() -> None:
    r = Random(Int(0))
    for _ in range(100):
        v = r.randint(Int(1), Int(10))._value
        assert 1 <= v <= 10


def test_randrange_single_arg() -> None:
    r = Random(Int(0))
    v = r.randrange(Int(10))._value
    assert 0 <= v < 10


def test_randrange_start_stop() -> None:
    r = Random(Int(0))
    v = r.randrange(Int(5), Int(15))._value
    assert 5 <= v < 15


def test_randrange_start_stop_step() -> None:
    r = Random(Int(0))
    v = r.randrange(Int(0), Int(20), Int(5))._value
    assert v in {0, 5, 10, 15}


def test_getrandbits() -> None:
    from poop.types.int import Int as _Int

    r = Random(Int(0))
    v = r.getrandbits(Int(8))
    assert isinstance(v, _Int)
    assert 0 <= v._value < 256


def test_randbytes_returns_poop_bytes_of_length() -> None:
    from poop.types.bytes import Bytes

    r = Random(Int(0))
    result = r.randbytes(Int(4))
    assert isinstance(result, Bytes)
    assert len(result._value) == 4


# --- Collection draws (simple) ---


def test_choice_returns_an_element_from_list() -> None:
    from poop.types.list import List

    r = Random(Int(0))
    coll = List(Int(1), Int(2), Int(3))
    picked = r.choice(coll)
    assert picked in (Int(1), Int(2), Int(3))


def test_choice_returns_poop_element() -> None:
    from poop.types.list import List

    r = Random(Int(0))
    coll = List(Int(10), Int(20), Int(30))
    picked = r.choice(coll)
    assert isinstance(picked, Int)


def test_choice_deterministic_with_seed() -> None:
    from poop.types.list import List

    coll = List(Int(1), Int(2), Int(3), Int(4), Int(5))
    a = Random(Int(42)).choice(coll)
    b = Random(Int(42)).choice(coll)
    assert isinstance(a, Int)
    assert isinstance(b, Int)
    assert a._value == b._value


def test_shuffle_mutates_list_in_place() -> None:
    from poop.types.list import List
    from poop.types.none import none

    r = Random(Int(0))
    coll = List(Int(1), Int(2), Int(3), Int(4), Int(5))
    values_before = sorted(cast(Int, x)._value for x in coll._items)
    result = r.shuffle(coll)
    values_after = sorted(cast(Int, x)._value for x in coll._items)
    assert result is none
    assert values_after == values_before  # same elements, order may differ


def test_shuffle_is_deterministic_with_seed() -> None:
    from poop.types.list import List

    a = List(Int(1), Int(2), Int(3), Int(4), Int(5))
    b = List(Int(1), Int(2), Int(3), Int(4), Int(5))
    Random(Int(42)).shuffle(a)
    Random(Int(42)).shuffle(b)
    a_order = [cast(Int, x)._value for x in a._items]
    b_order = [cast(Int, x)._value for x in b._items]
    assert a_order == b_order


# --- Collection draws (weighted) ---


def test_choices_default_k_is_one() -> None:
    from poop.types.list import List

    r = Random(Int(0))
    result = r.choices(List(Int(1), Int(2), Int(3)))
    assert isinstance(result, List)
    assert len(result._items) == 1


def test_choices_with_k() -> None:
    from poop.types.list import List

    r = Random(Int(0))
    result = r.choices(List(Int(1), Int(2), Int(3)), k=Int(5))
    assert len(result._items) == 5
    for item in result._items:
        assert cast(Int, item)._value in (1, 2, 3)


def test_choices_with_weights_skews_distribution() -> None:
    from poop.types.list import List

    r = Random(Int(42))
    population = List(Int(1), Int(2))
    weights = List(Int(0), Int(1))  # Always pick 2
    result = r.choices(population, weights=weights, k=Int(20))
    for item in result._items:
        assert cast(Int, item)._value == 2


def test_sample_returns_k_without_replacement() -> None:
    from poop.types.list import List

    r = Random(Int(0))
    population = List(Int(1), Int(2), Int(3), Int(4), Int(5))
    result = r.sample(population, Int(3))
    assert isinstance(result, List)
    assert len(result._items) == 3
    # No duplicates
    values = [cast(Int, item)._value for item in result._items]
    assert len(set(values)) == 3


def test_sample_with_counts() -> None:
    from poop.types.list import List

    r = Random(Int(0))
    # population [a, b] with counts [3, 0]: sample only from 'a' (treats as [a,a,a])
    population = List(Int(1), Int(2))
    counts = List(Int(3), Int(0))
    result = r.sample(population, Int(2), counts=counts)
    for item in result._items:
        assert cast(Int, item)._value == 1
