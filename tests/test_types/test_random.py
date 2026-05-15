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
