import pytest

from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str
from poop.types.tuple import Tuple


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


def test_pow_negative_base_fractional_exponent_returns_complex() -> None:
    result = Int(-8) ** Float(0.5)
    assert isinstance(result, Complex)
    assert result == Complex((-8) ** 0.5)


def test_pow_with_modulus_rejects_float_exponent() -> None:
    with pytest.raises(TypeError, match="all arguments are integers"):
        Int(2).__pow__(Float(0.5), Int(3))


def test_eq_returns_boolean() -> None:
    assert Int(5).__eq__(Int(5)) is true
    assert Int(5).__eq__(Int(6)) is false


def test_eq_with_non_int_returns_false() -> None:
    assert Int(5).__eq__(42) is false


def test_ne_returns_boolean() -> None:
    assert Int(5).__ne__(Int(6)) is true
    assert Int(5).__ne__(Int(5)) is false


def test_ne_with_non_int_returns_true() -> None:
    assert Int(5).__ne__(42) is true


def test_lt_returns_boolean() -> None:
    assert Int(3).__lt__(Int(5)) is true
    assert Int(5).__lt__(Int(3)) is false


def test_le_returns_boolean() -> None:
    assert Int(3).__le__(Int(3)) is true
    assert Int(5).__le__(Int(3)) is false


def test_gt_returns_boolean() -> None:
    assert Int(5).__gt__(Int(3)) is true
    assert Int(3).__gt__(Int(5)) is false


def test_ge_returns_boolean() -> None:
    assert Int(5).__ge__(Int(5)) is true
    assert Int(3).__ge__(Int(5)) is false


def test_hashable() -> None:
    assert hash(Int(42)) == hash(42)


def test_is_none_inherited() -> None:
    assert Int(1).is_none() is false


def test_class_name() -> None:
    assert Int(1).class_name() == Str("int")


@pytest.mark.parametrize("value", [0, 1, -1, 100])
def test_roundtrip_str(value: int) -> None:
    assert str(Int(value)) == str(value)


def test_abs_positive() -> None:
    assert Int(5).abs() == Int(5)


def test_abs_negative() -> None:
    assert Int(-5).abs() == Int(5)


def test_dunder_abs() -> None:
    assert abs(Int(-3)) == Int(3)


def test_truediv_returns_float() -> None:
    result = Int(7) / Int(2)
    assert isinstance(result, Float)
    assert result._value == pytest.approx(3.5)


def test_lshift() -> None:
    assert Int(1) << Int(3) == Int(8)


def test_rshift() -> None:
    assert Int(8) >> Int(2) == Int(2)


def test_bitwise_and() -> None:
    assert Int(0b1100) & Int(0b1010) == Int(0b1000)


def test_bitwise_or() -> None:
    assert Int(0b1100) | Int(0b1010) == Int(0b1110)


def test_bitwise_xor() -> None:
    assert Int(0b1100) ^ Int(0b1010) == Int(0b0110)


def test_round_returns_self() -> None:
    assert Int(5).round() == Int(5)


def test_round_with_poop_int_ndigits() -> None:
    assert Int(123).round(Int(-1)) == Int(120)
    assert Int(125).round(Int(-2)) == Int(100)


def test_round_accepts_poop_none() -> None:
    from poop.types.none import none

    assert Int(5).round(none) == Int(5)


def test_bit_count() -> None:
    assert Int(0b1011).bit_count() == Int(3)


def test_bit_length() -> None:
    assert Int(8).bit_length() == Int(4)


def test_is_integer_always_true() -> None:
    assert Int(42).is_integer() is true


def test_int_constructor_identity() -> None:
    from poop.transformers.int import _poop_int_from

    n = Int(3)
    assert _poop_int_from(n) is n


def test_float_constructor() -> None:
    from poop.transformers.float import _poop_float_from

    result = _poop_float_from(Int(3))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(3.0)


def test_complex_constructor() -> None:
    from poop.transformers.complex import _poop_complex_from

    assert _poop_complex_from(Int(3)) == Complex(3 + 0j)


def test_real_returns_self() -> None:
    n = Int(5)
    assert n.real is n


def test_imag_returns_zero() -> None:
    assert Int(5).imag == Int(0)


def test_numerator_returns_self() -> None:
    n = Int(7)
    assert n.numerator is n


def test_denominator_returns_one() -> None:
    assert Int(5).denominator == Int(1)


def test_conjugate_returns_self() -> None:
    n = Int(5)
    assert n.conjugate() is n


def test_as_integer_ratio() -> None:
    assert Int(5).as_integer_ratio() == Tuple(Int(5), Int(1))


def test_to_bytes_big_endian() -> None:
    assert Int(255).to_bytes(Int(2), Str("big")) == Bytes(b"\x00\xff")


def test_to_bytes_little_endian() -> None:
    assert Int(255).to_bytes(Int(2), Str("little")) == Bytes(b"\xff\x00")


def test_bin_returns_binary_string() -> None:
    assert Int(10).bin() == Str("0b1010")


def test_hex_returns_hex_string() -> None:
    assert Int(255).hex() == Str("0xff")


def test_oct_returns_octal_string() -> None:
    assert Int(8).oct() == Str("0o10")


def test_chr_returns_character() -> None:
    assert Int(65).chr() == Str("A")


def test_pow_method() -> None:
    assert Int(2).pow(Int(10)) == Int(1024)


def test_from_bytes_big_endian() -> None:
    assert Int.from_bytes(Bytes(b"\x00\xff"), Str("big")) == Int(255)


def test_from_bytes_little_endian() -> None:
    assert Int.from_bytes(Bytes(b"\xff\x00"), Str("little")) == Int(255)


def test_from_bytes_roundtrips_with_to_bytes() -> None:
    n = Int(12345)
    b = n.to_bytes(Int(4), Str("big"))
    assert Int.from_bytes(b, Str("big")) == n


# --- Cross-POOP-type numeric equality (proposal 86) ---


def test_eq_with_float_same_value() -> None:
    from poop.types.float import Float

    assert Int(1) == Float(1.0)
    assert Int(2) != Float(2.5)


def test_ne_with_float_same_value() -> None:
    from poop.types.float import Float

    assert (Int(1) != Float(1.0)) is false
    assert (Int(2) != Float(2.5)) is true


def test_ne_with_non_numeric_returns_true() -> None:
    assert (Int(5) != Str("5")) is true


def test_arith_with_float_operand_promotes_to_float() -> None:
    from poop.types.float import Float

    for op, expected_val in [
        (Int(1) + Float(2.5), 3.5),
        (Int(5) - Float(2.0), 3.0),
        (Int(3) * Float(2.0), 6.0),
        (Int(5) // Float(2.0), 2.0),
        (Int(5) % Float(2.0), 1.0),
    ]:
        assert isinstance(op, Float)
        assert op == Float(expected_val)


def test_pow_with_modulus() -> None:
    # 3-arg modular exponentiation (proposal 83).
    assert Int(5).pow(Int(3), Int(7)) == Int(6)
    assert Int(2).__pow__(Int(10), Int(1000)) == Int(24)
