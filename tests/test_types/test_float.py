from poop.types.float import Float


def test_str() -> None:
    assert str(Float(3.14)) == "3.14"


def test_repr_delegates_to_str() -> None:
    assert repr(Float(3.14)) == "3.14"


def test_float_conversion() -> None:
    assert float(Float(2.5)) == 2.5


def test_bool_nonzero_is_true() -> None:
    assert bool(Float(1.0)) is True


def test_bool_zero_is_false() -> None:
    assert bool(Float(0.0)) is False


def test_negated() -> None:
    assert Float(3.0).negated() == Float(-3.0)


def test_negated_negative() -> None:
    assert Float(-2.5).negated() == Float(2.5)


def test_max_returns_larger() -> None:
    assert Float(1.5).max(Float(2.5)) == Float(2.5)
    assert Float(2.5).max(Float(1.5)) == Float(2.5)


def test_min_returns_smaller() -> None:
    assert Float(1.5).min(Float(2.5)) == Float(1.5)
    assert Float(2.5).min(Float(1.5)) == Float(1.5)


def test_add() -> None:
    assert Float(1.5) + Float(2.5) == Float(4.0)


def test_sub() -> None:
    assert Float(5.0) - Float(2.0) == Float(3.0)


def test_mul() -> None:
    assert Float(2.0) * Float(3.0) == Float(6.0)


def test_truediv() -> None:
    assert Float(7.0) / Float(2.0) == Float(3.5)


def test_mod() -> None:
    assert Float(7.0) % Float(3.0) == Float(1.0)


def test_pow() -> None:
    assert Float(2.0) ** Float(3.0) == Float(8.0)


def test_eq() -> None:
    assert Float(1.5) == Float(1.5)
    assert Float(1.5) != Float(2.5)


def test_eq_with_non_float_returns_not_implemented() -> None:
    assert Float(1.5).__eq__(1.5) is NotImplemented


def test_lt() -> None:
    assert Float(1.0) < Float(2.0)
    assert not (Float(2.0) < Float(1.0))


def test_le() -> None:
    assert Float(1.0) <= Float(1.0)
    assert Float(1.0) <= Float(2.0)


def test_gt() -> None:
    assert Float(2.0) > Float(1.0)
    assert not (Float(1.0) > Float(2.0))


def test_ge() -> None:
    assert Float(2.0) >= Float(2.0)
    assert Float(2.0) >= Float(1.0)


def test_hashable() -> None:
    assert hash(Float(1.5)) == hash(1.5)


def test_is_none_inherited() -> None:
    from poop.types.boolean import false

    assert Float(1.0).is_none() is false


def test_class_name() -> None:
    assert Float(1.0).class_name() == "Float"
