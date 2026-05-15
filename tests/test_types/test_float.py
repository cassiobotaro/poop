import pytest

from poop.types.boolean import false, true
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str


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


def test_eq_returns_boolean() -> None:
    assert Float(1.5).__eq__(Float(1.5)) is true
    assert Float(1.5).__eq__(Float(2.5)) is false


def test_eq_with_non_float_returns_false() -> None:
    assert Float(1.5).__eq__(1.5) is false


def test_ne_returns_boolean() -> None:
    assert Float(1.5).__ne__(Float(2.5)) is true
    assert Float(1.5).__ne__(Float(1.5)) is false


def test_ne_with_non_float_returns_true() -> None:
    assert Float(1.5).__ne__(1.5) is true


def test_lt_returns_boolean() -> None:
    assert Float(1.0).__lt__(Float(2.0)) is true
    assert Float(2.0).__lt__(Float(1.0)) is false


def test_le_returns_boolean() -> None:
    assert Float(1.0).__le__(Float(1.0)) is true
    assert Float(2.0).__le__(Float(1.0)) is false


def test_gt_returns_boolean() -> None:
    assert Float(2.0).__gt__(Float(1.0)) is true
    assert Float(1.0).__gt__(Float(2.0)) is false


def test_ge_returns_boolean() -> None:
    assert Float(2.0).__ge__(Float(2.0)) is true
    assert Float(1.0).__ge__(Float(2.0)) is false


def test_hashable() -> None:
    assert hash(Float(1.5)) == hash(1.5)


def test_is_none_inherited() -> None:
    assert Float(1.0).is_none() is false


def test_class_name() -> None:
    assert Float(1.0).class_name() == Str("float")


def test_abs_positive() -> None:
    assert Float(3.5).abs() == Float(3.5)


def test_abs_negative() -> None:
    assert Float(-3.5).abs() == Float(3.5)


def test_dunder_abs() -> None:
    assert abs(Float(-2.0)) == Float(2.0)


def test_round_no_digits_returns_int() -> None:
    assert Float(2.5).round() == Int(2)
    assert Float(3.5).round() == Int(4)


def test_round_with_digits_returns_float() -> None:
    assert Float(3.14159).round(Int(2)) == Float(3.14)
    assert Float(3.456).round(Int(1)) == Float(3.5)


def test_round_accepts_poop_none() -> None:
    from poop.types.none import none

    assert Float(2.5).round(none) == Int(2)


def test_int_conversion() -> None:
    assert int(Float(3.9)) == 3


def test_complex_constructor() -> None:
    from poop.transformers.complex import _poop_complex_from

    assert _poop_complex_from(Float(2.5)) == Complex(2.5 + 0j)


def test_is_integer_true() -> None:
    assert Float(3.0).is_integer() is true


def test_is_integer_false() -> None:
    assert Float(3.5).is_integer() is false


def test_floordiv() -> None:
    assert Float(7.0) // Float(2.0) == Float(3.0)


def test_int_truncates() -> None:
    from poop.transformers.int import _poop_int_from

    assert _poop_int_from(Float(3.7)) == Int(3)
    assert _poop_int_from(Float(-2.9)) == Int(-2)


def test_float_constructor_identity() -> None:
    from poop.transformers.float import _poop_float_from

    f = Float(1.5)
    assert _poop_float_from(f) is f


def test_conjugate_returns_self() -> None:
    f = Float(3.5)
    assert f.conjugate() is f


def test_hex_returns_str() -> None:
    assert Float(1.0).hex() == Str("0x1.0000000000000p+0")


def test_real_returns_self() -> None:
    f = Float(2.5)
    assert f.real is f


def test_imag_returns_zero() -> None:
    assert Float(2.5).imag == Float(0.0)


def test_as_integer_ratio() -> None:
    n, d = Float(0.5).as_integer_ratio()._items
    assert n == Int(1)
    assert d == Int(2)


def test_pow_method() -> None:
    assert Float(2.0).pow(Float(3.0)) == Float(8.0)


def test_fromhex_parses_hex_string() -> None:
    result = Float.fromhex(Str("0x1.8p+0"))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(1.5)


def test_fromhex_roundtrips_with_hex() -> None:
    f = Float(3.14)
    assert Float.fromhex(f.hex()) == f
