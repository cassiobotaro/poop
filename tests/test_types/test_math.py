import math as _math

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.float import Float
from poop.types.int import Int
from poop.types.math import Math
from poop.types.tuple import Tuple


def test_constant_pi_present() -> None:
    assert isinstance(Math.pi, Float)
    assert Math.pi._value == _math.pi


def test_sqrt_returns_poop_float() -> None:
    result = Math.sqrt(Float(4.0))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(2.0)


def test_math_reachable_via_interpreter() -> None:
    Interpreter().run_source("Math.sqrt(2.0).print()")


# --- Number theory ---


def test_factorial_returns_poop_int() -> None:
    result = Math.factorial(Int(5))
    assert isinstance(result, Int)
    assert result._value == 120


def test_gcd_varargs() -> None:
    assert Math.gcd(Int(12), Int(18))._value == 6
    assert Math.gcd(Int(12), Int(18), Int(24))._value == 6
    assert isinstance(Math.gcd(Int(12), Int(18)), Int)


def test_lcm_varargs() -> None:
    assert Math.lcm(Int(4), Int(6))._value == 12
    assert Math.lcm(Int(2), Int(3), Int(5))._value == 30


def test_comb() -> None:
    assert Math.comb(Int(5), Int(2))._value == 10
    assert isinstance(Math.comb(Int(5), Int(2)), Int)


def test_perm_with_k() -> None:
    assert Math.perm(Int(5), Int(2))._value == 20


def test_perm_default_k_returns_factorial() -> None:
    assert Math.perm(Int(4))._value == 24


def test_isqrt() -> None:
    assert Math.isqrt(Int(17))._value == 4
    assert isinstance(Math.isqrt(Int(17)), Int)


# --- Trigonometric ---


def test_sin_cos_tan() -> None:
    assert Math.sin(Float(0.0))._value == pytest.approx(0.0)
    assert Math.cos(Float(0.0))._value == pytest.approx(1.0)
    assert Math.tan(Float(0.0))._value == pytest.approx(0.0)


def test_sin_returns_poop_float() -> None:
    assert isinstance(Math.sin(Float(1.0)), Float)


def test_asin_acos_atan() -> None:
    assert Math.asin(Float(0.0))._value == pytest.approx(0.0)
    assert Math.acos(Float(1.0))._value == pytest.approx(0.0)
    assert Math.atan(Float(0.0))._value == pytest.approx(0.0)


def test_atan2() -> None:
    assert Math.atan2(Float(1.0), Float(1.0))._value == pytest.approx(_math.pi / 4)
    assert isinstance(Math.atan2(Float(1.0), Float(1.0)), Float)


# --- Hyperbolic ---


def test_sinh_cosh_tanh_at_zero() -> None:
    assert Math.sinh(Float(0.0))._value == pytest.approx(0.0)
    assert Math.cosh(Float(0.0))._value == pytest.approx(1.0)
    assert Math.tanh(Float(0.0))._value == pytest.approx(0.0)


def test_sinh_returns_poop_float() -> None:
    assert isinstance(Math.sinh(Float(1.0)), Float)


def test_asinh_acosh_atanh() -> None:
    assert Math.asinh(Float(0.0))._value == pytest.approx(0.0)
    assert Math.acosh(Float(1.0))._value == pytest.approx(0.0)
    assert Math.atanh(Float(0.0))._value == pytest.approx(0.0)


# --- Exp / log / power ---


def test_exp_family() -> None:
    assert Math.exp(Float(0.0))._value == pytest.approx(1.0)
    assert Math.expm1(Float(0.0))._value == pytest.approx(0.0)
    assert Math.exp2(Float(3.0))._value == pytest.approx(8.0)


def test_log_default_base_natural() -> None:
    assert Math.log(Float(_math.e))._value == pytest.approx(1.0)
    assert isinstance(Math.log(Float(_math.e)), Float)


def test_log_with_explicit_base() -> None:
    assert Math.log(Float(8.0), Float(2.0))._value == pytest.approx(3.0)


def test_log2_log10_log1p() -> None:
    assert Math.log2(Float(8.0))._value == pytest.approx(3.0)
    assert Math.log10(Float(100.0))._value == pytest.approx(2.0)
    assert Math.log1p(Float(0.0))._value == pytest.approx(0.0)


def test_cbrt() -> None:
    assert Math.cbrt(Float(8.0))._value == pytest.approx(2.0)
    assert Math.cbrt(Float(64.0))._value == pytest.approx(4.0)


def test_pow_returns_float() -> None:
    result = Math.pow(Float(2.0), Float(10.0))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(1024.0)


# --- Rounding & float decomposition ---


def test_floor_ceil_trunc_return_int() -> None:
    assert Math.floor(Float(3.7))._value == 3
    assert isinstance(Math.floor(Float(3.7)), Int)
    assert Math.ceil(Float(3.2))._value == 4
    assert isinstance(Math.ceil(Float(3.2)), Int)
    assert Math.trunc(Float(-3.7))._value == -3
    assert isinstance(Math.trunc(Float(-3.7)), Int)


def test_modf_returns_tuple_of_floats() -> None:
    result = Math.modf(Float(3.75))
    assert isinstance(result, Tuple)
    frac, integ = result._items
    assert isinstance(frac, Float)
    assert isinstance(integ, Float)
    assert frac._value == pytest.approx(0.75)
    assert integ._value == pytest.approx(3.0)


def test_frexp_returns_tuple_of_float_and_int() -> None:
    result = Math.frexp(Float(8.0))
    assert isinstance(result, Tuple)
    mantissa, exponent = result._items
    assert isinstance(mantissa, Float)
    assert isinstance(exponent, Int)
    assert mantissa._value == pytest.approx(0.5)
    assert exponent._value == 4


def test_ldexp() -> None:
    assert Math.ldexp(Float(0.5), Int(4))._value == pytest.approx(8.0)
    assert isinstance(Math.ldexp(Float(0.5), Int(4)), Float)


# --- Angular conversion ---


def test_degrees() -> None:
    assert Math.degrees(Float(_math.pi))._value == pytest.approx(180.0)
    assert isinstance(Math.degrees(Float(_math.pi)), Float)


def test_radians() -> None:
    assert Math.radians(Float(180.0))._value == pytest.approx(_math.pi)
    assert isinstance(Math.radians(Float(180.0)), Float)


# --- Float utilities ---


def test_fabs() -> None:
    assert Math.fabs(Float(-3.5))._value == pytest.approx(3.5)
    assert Math.fabs(Float(3.5))._value == pytest.approx(3.5)
    assert isinstance(Math.fabs(Float(-1.0)), Float)


def test_copysign() -> None:
    assert Math.copysign(Float(3.0), Float(-1.0))._value == pytest.approx(-3.0)
    assert Math.copysign(Float(-3.0), Float(1.0))._value == pytest.approx(3.0)


def test_fmod() -> None:
    assert Math.fmod(Float(7.0), Float(3.0))._value == pytest.approx(1.0)
    assert isinstance(Math.fmod(Float(7.0), Float(3.0)), Float)


def test_remainder() -> None:
    assert Math.remainder(Float(7.0), Float(3.0))._value == pytest.approx(1.0)


def test_fma() -> None:
    assert Math.fma(Float(2.0), Float(3.0), Float(4.0))._value == pytest.approx(10.0)
    assert isinstance(Math.fma(Float(2.0), Float(3.0), Float(4.0)), Float)


def test_ulp_positive() -> None:
    result = Math.ulp(Float(1.0))
    assert isinstance(result, Float)
    assert result._value > 0.0


def test_nextafter_no_steps() -> None:
    result = Math.nextafter(Float(1.0), Float(2.0))
    assert isinstance(result, Float)
    assert result._value > 1.0


def test_nextafter_with_steps() -> None:
    result = Math.nextafter(Float(1.0), Float(2.0), steps=Int(3))
    assert isinstance(result, Float)
    assert result._value > Math.nextafter(Float(1.0), Float(2.0))._value


# --- Predicates ---


def test_isfinite() -> None:
    assert Math.isfinite(Float(1.0)) is true
    assert Math.isfinite(Float(float("inf"))) is false
    assert Math.isfinite(Float(float("nan"))) is false


def test_isinf() -> None:
    assert Math.isinf(Float(float("inf"))) is true
    assert Math.isinf(Float(-float("inf"))) is true
    assert Math.isinf(Float(1.0)) is false


def test_isnan() -> None:
    assert Math.isnan(Float(float("nan"))) is true
    assert Math.isnan(Float(1.0)) is false


def test_isclose_default_tolerances() -> None:
    assert Math.isclose(Float(1.0), Float(1.0)) is true
    assert Math.isclose(Float(1.0), Float(2.0)) is false


def test_isclose_with_rel_tol() -> None:
    assert Math.isclose(Float(100.0), Float(101.0), rel_tol=Float(0.02)) is true
    assert Math.isclose(Float(100.0), Float(101.0), rel_tol=Float(1e-9)) is false


def test_isclose_with_abs_tol() -> None:
    assert Math.isclose(Float(0.0), Float(1e-12), abs_tol=Float(1e-9)) is true
    assert Math.isclose(Float(0.0), Float(1e-12)) is false


# --- Iterable aggregates ---


def test_fsum() -> None:
    from poop.types.list import List

    result = Math.fsum(List(Float(0.1), Float(0.2), Float(0.3)))
    assert isinstance(result, Float)
    assert Math.isclose(result, Float(0.6)) is true


def test_prod_default_start_int() -> None:
    from poop.types.list import List

    result = Math.prod(List(Int(2), Int(3), Int(4)))
    assert isinstance(result, Int)
    assert result._value == 24


def test_prod_float_input_returns_float() -> None:
    from poop.types.list import List

    result = Math.prod(List(Float(2.0), Float(3.0), Float(4.0)))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(24.0)


def test_prod_with_start() -> None:
    from poop.types.list import List

    result = Math.prod(List(Int(2), Int(3)), start=Int(10))
    assert isinstance(result, Int)
    assert result._value == 60


def test_sumprod() -> None:
    from poop.types.list import List

    p = List(Int(1), Int(2), Int(3))
    q = List(Int(4), Int(5), Int(6))
    result = Math.sumprod(p, q)
    assert isinstance(result, Int)
    assert result._value == 32  # 1*4 + 2*5 + 3*6


def test_dist() -> None:
    from poop.types.tuple import Tuple as _Tuple

    p = _Tuple(Float(0.0), Float(0.0))
    q = _Tuple(Float(3.0), Float(4.0))
    result = Math.dist(p, q)
    assert isinstance(result, Float)
    assert result._value == pytest.approx(5.0)


def test_hypot_2d() -> None:
    result = Math.hypot(Float(3.0), Float(4.0))
    assert isinstance(result, Float)
    assert result._value == pytest.approx(5.0)


def test_hypot_n_dim() -> None:
    result = Math.hypot(Float(3.0), Float(4.0), Float(12.0))
    assert result._value == pytest.approx(13.0)


def test_hypot_accepts_int() -> None:
    result = Math.hypot(Int(3), Int(4))
    assert result._value == pytest.approx(5.0)


# --- Special functions ---


def test_erf_at_zero() -> None:
    assert Math.erf(Float(0.0))._value == pytest.approx(0.0)
    assert isinstance(Math.erf(Float(0.0)), Float)


def test_erfc_at_zero() -> None:
    assert Math.erfc(Float(0.0))._value == pytest.approx(1.0)


def test_gamma() -> None:
    assert Math.gamma(Float(1.0))._value == pytest.approx(1.0)
    assert Math.gamma(Float(5.0))._value == pytest.approx(24.0)  # gamma(n) == (n-1)!


def test_lgamma() -> None:
    assert Math.lgamma(Float(1.0))._value == pytest.approx(0.0)
    assert isinstance(Math.lgamma(Float(1.0)), Float)
