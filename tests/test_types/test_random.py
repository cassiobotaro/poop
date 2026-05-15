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
