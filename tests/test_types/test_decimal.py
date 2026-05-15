import decimal as _decimal

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import Boolean, false, true
from poop.types.decimal import Context, Decimal, Decimal_
from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import none
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_decimal_from_str() -> None:
    d = Decimal(Str("3.14"))
    assert isinstance(d, Decimal)


def test_decimal_from_int() -> None:
    d = Decimal(Int(42))
    assert d == Decimal(Str("42"))


def test_decimal_from_float() -> None:
    assert isinstance(Decimal(Float(0.5)), Decimal)


def test_decimal_from_tuple() -> None:
    d = Decimal(Tuple(Int(0), Tuple(Int(3), Int(1), Int(4)), Int(-2)))
    assert d == Decimal(Str("3.14"))


def test_decimal_add() -> None:
    assert Decimal(Str("1.5")) + Decimal(Str("2.5")) == Decimal(Str("4.0"))


def test_decimal_sub() -> None:
    assert Decimal(Str("4.0")) - Decimal(Str("1.5")) == Decimal(Str("2.5"))


def test_decimal_mul() -> None:
    assert Decimal(Str("2")) * Decimal(Str("3.5")) == Decimal(Str("7.0"))


def test_decimal_div() -> None:
    assert Decimal(Str("10")) / Decimal(Str("4")) == Decimal(Str("2.5"))


def test_decimal_floordiv() -> None:
    assert Decimal(Str("10")) // Decimal(Str("3")) == Decimal(Str("3"))


def test_decimal_mod() -> None:
    assert Decimal(Str("10")) % Decimal(Str("3")) == Decimal(Str("1"))


def test_decimal_pow() -> None:
    assert Decimal(Str("2")) ** Decimal(Str("10")) == Decimal(Str("1024"))


def test_decimal_neg() -> None:
    assert -Decimal(Str("3")) == Decimal(Str("-3"))


def test_decimal_abs() -> None:
    assert abs(Decimal(Str("-3"))) == Decimal(Str("3"))


def test_decimal_comparisons() -> None:
    a = Decimal(Str("1"))
    b = Decimal(Str("2"))
    assert (a < b) is true
    assert (b > a) is true
    assert (a <= a) is true
    assert (a >= a) is true


def test_decimal_quantize() -> None:
    d = Decimal(Str("3.14159"))
    assert d.quantize(Decimal(Str("0.01"))) == Decimal(Str("3.14"))


def test_decimal_quantize_with_rounding() -> None:
    d = Decimal(Str("3.146"))
    assert d.quantize(Decimal(Str("0.01")), Decimal_.ROUND_HALF_UP) == Decimal(
        Str("3.15")
    )


def test_decimal_normalize() -> None:
    assert Decimal(Str("1.00")).normalize() == Decimal(Str("1"))


def test_decimal_adjusted() -> None:
    assert Decimal(Str("123")).adjusted() == Int(2)


def test_decimal_as_tuple() -> None:
    t = Decimal(Str("3.14")).as_tuple()
    assert isinstance(t, Tuple)
    assert t.at(Int(0)) == Int(0)


def test_decimal_as_integer_ratio() -> None:
    r = Decimal(Str("0.25")).as_integer_ratio()
    assert isinstance(r, Tuple)
    assert r.at(Int(0)) == Int(1)
    assert r.at(Int(1)) == Int(4)


def test_decimal_is_finite() -> None:
    assert Decimal(Str("3.14")).is_finite() is true
    assert Decimal(Str("Infinity")).is_finite() is false


def test_decimal_is_infinite() -> None:
    assert Decimal(Str("Infinity")).is_infinite() is true
    assert Decimal(Str("0")).is_infinite() is false


def test_decimal_is_nan() -> None:
    assert Decimal(Str("NaN")).is_nan() is true
    assert Decimal(Str("0")).is_nan() is false


def test_decimal_is_signed() -> None:
    assert Decimal(Str("-1")).is_signed() is true
    assert Decimal(Str("1")).is_signed() is false


def test_decimal_is_zero() -> None:
    assert Decimal(Str("0")).is_zero() is true
    assert Decimal(Str("1")).is_zero() is false


def test_decimal_sqrt() -> None:
    assert Decimal(Str("16")).sqrt() == Decimal(Str("4"))


def test_decimal_ln() -> None:
    val = Decimal(Str("1")).ln()
    assert isinstance(val, Decimal)
    assert val.is_zero() is true


def test_decimal_log10() -> None:
    assert Decimal(Str("1000")).log10() == Decimal(Str("3"))


def test_decimal_exp() -> None:
    assert isinstance(Decimal(Str("1")).exp(), Decimal)


def test_decimal_to_integral_value() -> None:
    assert Decimal(Str("3.7")).to_integral_value(Decimal_.ROUND_FLOOR) == Decimal(
        Str("3")
    )


def test_decimal_copy_abs() -> None:
    assert Decimal(Str("-3")).copy_abs() == Decimal(Str("3"))


def test_decimal_copy_negate() -> None:
    assert Decimal(Str("3")).copy_negate() == Decimal(Str("-3"))


def test_decimal_compare() -> None:
    assert Decimal(Str("1")).compare(Decimal(Str("2"))) == Decimal(Str("-1"))


def test_decimal_hash_and_equality() -> None:
    a = Decimal(Str("1.5"))
    b = Decimal(Str("1.5"))
    assert a == b
    assert hash(a) == hash(b)


def test_decimal_namespace_class_attribute() -> None:
    assert Decimal_.Decimal is Decimal


def test_decimal_rounding_constants_are_str() -> None:
    assert Decimal_.ROUND_UP == Str(_decimal.ROUND_UP)
    assert Decimal_.ROUND_DOWN == Str(_decimal.ROUND_DOWN)
    assert Decimal_.ROUND_HALF_UP == Str(_decimal.ROUND_HALF_UP)
    assert Decimal_.ROUND_HALF_DOWN == Str(_decimal.ROUND_HALF_DOWN)
    assert Decimal_.ROUND_HALF_EVEN == Str(_decimal.ROUND_HALF_EVEN)
    assert Decimal_.ROUND_CEILING == Str(_decimal.ROUND_CEILING)
    assert Decimal_.ROUND_FLOOR == Str(_decimal.ROUND_FLOOR)
    assert Decimal_.ROUND_05UP == Str(_decimal.ROUND_05UP)


def test_decimal_signal_classes_exposed() -> None:
    assert Decimal_.InvalidOperation is _decimal.InvalidOperation
    assert Decimal_.DivisionByZero is _decimal.DivisionByZero
    assert Decimal_.Overflow is _decimal.Overflow
    assert Decimal_.Underflow is _decimal.Underflow
    assert Decimal_.Inexact is _decimal.Inexact
    assert Decimal_.Rounded is _decimal.Rounded
    assert Decimal_.Subnormal is _decimal.Subnormal
    assert Decimal_.Clamped is _decimal.Clamped
    assert Decimal_.FloatOperation is _decimal.FloatOperation
    assert Decimal_.DecimalException is _decimal.DecimalException


def test_decimal_getcontext_returns_context() -> None:
    ctx = Decimal_.getcontext()
    assert isinstance(ctx, Context)
    assert isinstance(ctx.prec, Int)


def test_decimal_setcontext_returns_none() -> None:
    ctx = Decimal_.getcontext()
    assert Decimal_.setcontext(ctx) is none


def test_decimal_localcontext_as_with() -> None:
    with Decimal_.localcontext() as ctx:
        assert isinstance(ctx, Context)


def test_decimal_division_by_zero_raises() -> None:
    with pytest.raises(_decimal.DivisionByZero):
        Decimal(Str("1")) / Decimal(Str("0"))


def test_decimal_in_default_namespace() -> None:
    from poop.transformers import DEFAULT_NAMESPACE

    assert DEFAULT_NAMESPACE["decimal"] is Decimal_
    assert DEFAULT_NAMESPACE["Decimal"] is Decimal
    assert DEFAULT_NAMESPACE["Context"] is Context


def test_decimal_reachable_via_interpreter() -> None:
    Interpreter().run_source('Decimal("3.14").print()')


def test_context_create_decimal() -> None:
    ctx = Decimal_.getcontext()
    d = ctx.create_decimal(Str("1.5"))
    assert isinstance(d, Decimal)


def test_decimal_str_returns_str() -> None:
    assert str(Decimal(Str("3.14"))) == "3.14"


def test_decimal_boolean_methods_return_boolean() -> None:
    assert isinstance(Decimal(Str("1")).is_finite(), Boolean)
