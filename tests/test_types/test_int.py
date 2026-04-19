import pytest

from poop.types.int import Int


def test_str() -> None:
    assert str(Int(42)) == "42"


def test_repr_delegates_to_str() -> None:
    assert repr(Int(42)) == "42"


def test_int_conversion() -> None:
    assert int(Int(7)) == 7


def test_bool_nonzero_is_true() -> None:
    assert bool(Int(1)) is True


def test_bool_zero_is_false() -> None:
    assert bool(Int(0)) is False


def test_negated() -> None:
    assert Int(3).negated() == Int(-3)


def test_negated_negative() -> None:
    assert Int(-5).negated() == Int(5)


def test_bit_invert() -> None:
    assert Int(0).bit_invert() == Int(-1)
    assert Int(1).bit_invert() == Int(-2)


def test_times_repeat() -> None:
    calls: list[None] = []
    Int(3).times_repeat(lambda: calls.append(None))
    assert len(calls) == 3


def test_times_repeat_zero() -> None:
    calls: list[None] = []
    Int(0).times_repeat(lambda: calls.append(None))
    assert calls == []


def test_to_do() -> None:
    results: list[int] = []
    Int(1).to_do(Int(4), lambda i: results.append(int(i)))
    assert results == [1, 2, 3, 4]


def test_max_returns_larger() -> None:
    assert Int(3).max(Int(7)) == Int(7)
    assert Int(7).max(Int(3)) == Int(7)


def test_min_returns_smaller() -> None:
    assert Int(3).min(Int(7)) == Int(3)
    assert Int(7).min(Int(3)) == Int(3)


def test_add() -> None:
    assert Int(2) + Int(3) == Int(5)


def test_sub() -> None:
    assert Int(5) - Int(2) == Int(3)


def test_mul() -> None:
    assert Int(3) * Int(4) == Int(12)


def test_floordiv() -> None:
    assert Int(7) // Int(2) == Int(3)


def test_mod() -> None:
    assert Int(7) % Int(3) == Int(1)


def test_pow() -> None:
    assert Int(2) ** Int(10) == Int(1024)


def test_eq() -> None:
    assert Int(5) == Int(5)
    assert Int(5) != Int(6)


def test_eq_with_non_int_returns_not_implemented() -> None:
    assert Int(5).__eq__(42) is NotImplemented


def test_lt() -> None:
    assert Int(3) < Int(5)
    assert not (Int(5) < Int(3))


def test_le() -> None:
    assert Int(3) <= Int(3)
    assert Int(3) <= Int(5)


def test_gt() -> None:
    assert Int(5) > Int(3)
    assert not (Int(3) > Int(5))


def test_ge() -> None:
    assert Int(5) >= Int(5)
    assert Int(5) >= Int(3)


def test_hashable() -> None:
    assert hash(Int(42)) == hash(42)


def test_is_none_inherited() -> None:
    from poop.types.boolean import false

    assert Int(1).is_none() is false


def test_class_name() -> None:
    assert Int(1).class_name() == "Int"


@pytest.mark.parametrize("value", [0, 1, -1, 100])
def test_roundtrip_str(value: int) -> None:
    assert str(Int(value)) == str(value)
