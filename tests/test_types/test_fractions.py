import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.decimal import Decimal
from poop.types.float import Float
from poop.types.fractions import Fraction, FractionsNamespace
from poop.types.int import Int
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- Construction ---


def test_fraction_zero_default() -> None:
    assert Fraction() == Fraction(Int(0), Int(1))


def test_fraction_two_args() -> None:
    f = Fraction(Int(3), Int(4))
    assert f.numerator == Int(3)
    assert f.denominator == Int(4)


def test_fraction_reduces_automatically() -> None:
    f = Fraction(Int(2), Int(4))
    assert f.numerator == Int(1)
    assert f.denominator == Int(2)


def test_fraction_from_string_slash_form() -> None:
    f = Fraction(Str("3/4"))
    assert f == Fraction(Int(3), Int(4))


def test_fraction_from_string_decimal_form() -> None:
    f = Fraction(Str("0.25"))
    assert f == Fraction(Int(1), Int(4))


def test_fraction_from_float_classmethod() -> None:
    f = Fraction.from_float(Float(0.5))
    assert f == Fraction(Int(1), Int(2))


def test_fraction_from_decimal_classmethod() -> None:
    f = Fraction.from_decimal(Decimal(Str("0.5")))
    assert f == Fraction(Int(1), Int(2))


def test_fraction_from_fraction_copy() -> None:
    original = Fraction(Int(3), Int(7))
    copy = Fraction(original)
    assert copy == original


def test_fraction_zero_denominator_raises() -> None:
    with pytest.raises(ZeroDivisionError):
        Fraction(Int(1), Int(0))


# --- Properties ---


def test_fraction_limit_denominator_default() -> None:
    f = Fraction.from_float(Float(3.141592653589793))
    limited = f.limit_denominator()
    assert isinstance(limited, Fraction)
    assert limited.denominator._value <= 1_000_000


def test_fraction_limit_denominator_explicit() -> None:
    f = Fraction.from_float(Float(3.14159))
    limited = f.limit_denominator(Int(10))
    assert limited == Fraction(Int(22), Int(7))


def test_fraction_as_integer_ratio() -> None:
    f = Fraction(Int(3), Int(4))
    result = f.as_integer_ratio()
    assert isinstance(result, Tuple)
    assert result.at(Int(0)) == Int(3)
    assert result.at(Int(1)) == Int(4)


# --- Arithmetic ---


def test_fraction_addition() -> None:
    a = Fraction(Int(1), Int(2))
    b = Fraction(Int(1), Int(3))
    result = a + b
    assert result == Fraction(Int(5), Int(6))
    assert isinstance(result, Fraction)


def test_fraction_subtraction() -> None:
    a = Fraction(Int(3), Int(4))
    b = Fraction(Int(1), Int(4))
    assert a - b == Fraction(Int(1), Int(2))


def test_fraction_multiplication() -> None:
    a = Fraction(Int(2), Int(3))
    b = Fraction(Int(3), Int(4))
    assert a * b == Fraction(Int(1), Int(2))


def test_fraction_truediv() -> None:
    a = Fraction(Int(1), Int(2))
    b = Fraction(Int(1), Int(4))
    assert a / b == Fraction(Int(2), Int(1))


def test_fraction_int_promotion_keeps_fraction() -> None:
    a = Fraction(Int(1), Int(2))
    result = a + Int(1)
    assert isinstance(result, Fraction)
    assert result == Fraction(Int(3), Int(2))


def test_fraction_float_promotion_returns_float() -> None:
    a = Fraction(Int(1), Int(2))
    result = a + Float(0.25)
    assert isinstance(result, Float)
    assert result == Float(0.75)


def test_fraction_neg() -> None:
    f = Fraction(Int(3), Int(4))
    assert -f == Fraction(Int(-3), Int(4))


def test_fraction_abs() -> None:
    f = Fraction(Int(-3), Int(4))
    assert abs(f) == Fraction(Int(3), Int(4))


def test_fraction_pow_int_returns_fraction() -> None:
    f = Fraction(Int(2), Int(3))
    result = f ** Int(2)
    assert result == Fraction(Int(4), Int(9))


def test_fraction_floordiv_returns_int() -> None:
    a = Fraction(Int(7), Int(3))
    b = Fraction(Int(1), Int(1))
    assert a // b == Int(2)


def test_fraction_floordiv_by_int() -> None:
    a = Fraction(Int(7), Int(2))
    assert a // Int(2) == Int(1)


def test_fraction_floordiv_by_float() -> None:
    a = Fraction(Int(7), Int(2))
    result = a // Float(2.0)
    assert isinstance(result, Float)


def test_fraction_radd_via_dunder() -> None:
    # Int/Float don't return NotImplemented for non-POOP types so the
    # `Int + Fraction` shortcut won't dispatch to __radd__; test the
    # dunder directly.
    assert Fraction(Int(1), Int(2)).__radd__(Int(1)) == Fraction(Int(3), Int(2))


def test_fraction_rsub_via_dunder() -> None:
    assert Fraction(Int(1), Int(2)).__rsub__(Int(1)) == Fraction(Int(1), Int(2))


def test_fraction_rmul_via_dunder() -> None:
    assert Fraction(Int(3), Int(4)).__rmul__(Int(2)) == Fraction(Int(3), Int(2))


def test_fraction_rtruediv_via_dunder() -> None:
    assert Fraction(Int(1), Int(2)).__rtruediv__(Int(1)) == Fraction(Int(2), Int(1))


def test_fraction_mod() -> None:
    a = Fraction(Int(7), Int(2))
    assert a % Fraction(Int(1), Int(1)) == Fraction(Int(1), Int(2))


def test_fraction_pow_fraction_exact() -> None:
    a = Fraction(Int(2), Int(1))
    result = a ** Fraction(Int(2), Int(1))
    assert isinstance(result, Fraction)


def test_fraction_pow_fraction_irrational() -> None:
    a = Fraction(Int(2), Int(1))
    result = a ** Fraction(Int(1), Int(2))
    # 2 ** 0.5 is irrational — promotes to Float.
    assert isinstance(result, Float)


def test_fraction_pow_float() -> None:
    a = Fraction(Int(2), Int(1))
    result = a ** Float(0.5)
    assert isinstance(result, Float)


def test_fraction_pos() -> None:
    f = Fraction(Int(3), Int(4))
    assert +f == f


def test_fraction_repr_matches_str() -> None:
    f = Fraction(Int(3), Int(4))
    assert repr(f) == str(f)


def test_fraction_hash_equal_to_same_value() -> None:
    assert hash(Fraction(Int(1), Int(2))) == hash(Fraction(Int(2), Int(4)))


# --- Comparison ---


def test_fraction_equal() -> None:
    assert Fraction(Int(1), Int(2)) == Fraction(Int(2), Int(4))


def test_fraction_lt_int() -> None:
    assert (Fraction(Int(1), Int(2)) < Int(1)) is true


def test_fraction_gt_int() -> None:
    assert (Fraction(Int(3), Int(2)) > Int(1)) is true


def test_fraction_compared_to_float() -> None:
    assert (Fraction(Int(1), Int(2)) == Float(0.5)) is false
    # Note: Fraction.__eq__ is exact; mixed comparison via Float
    # promotion isn't transitive — comparisons via <,>,<=,>= work.
    assert (Fraction(Int(1), Int(2)) >= Float(0.5)) is true


# --- Namespace ---


def test_fractions_namespace_exposes_class() -> None:
    assert FractionsNamespace.Fraction is Fraction


# --- Interpreter integration ---


def test_fraction_reachable_via_interpreter() -> None:
    Interpreter().run_source("Fraction(3, 4).print()")


def test_fraction_arithmetic_via_interpreter() -> None:
    Interpreter().run_source(
        "r = Fraction(1, 2) + Fraction(1, 3)\nr.numerator.print()\nr.denominator.print()"
    )


def test_fractions_namespace_reachable_via_interpreter() -> None:
    Interpreter().run_source("fractions.Fraction(1, 2).print()")
