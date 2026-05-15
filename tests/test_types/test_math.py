import math as _math

from poop.interpreter import Interpreter
from poop.types.float import Float
from poop.types.int import Int
from poop.types.math import Math


def test_constant_pi_present() -> None:
    assert isinstance(Math.PI, Float)
    assert Math.PI._value == _math.pi


def test_sqrt_returns_poop_float() -> None:
    result = Math.sqrt(Float(4.0))
    assert isinstance(result, Float)
    assert result._value == 2.0


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
    assert Math.sin(Float(0.0))._value == 0.0
    assert Math.cos(Float(0.0))._value == 1.0
    assert Math.tan(Float(0.0))._value == 0.0


def test_sin_returns_poop_float() -> None:
    assert isinstance(Math.sin(Float(1.0)), Float)


def test_asin_acos_atan() -> None:
    assert Math.asin(Float(0.0))._value == 0.0
    assert Math.acos(Float(1.0))._value == 0.0
    assert Math.atan(Float(0.0))._value == 0.0


def test_atan2() -> None:
    assert Math.atan2(Float(1.0), Float(1.0))._value == _math.pi / 4
    assert isinstance(Math.atan2(Float(1.0), Float(1.0)), Float)


# --- Hyperbolic ---


def test_sinh_cosh_tanh_at_zero() -> None:
    assert Math.sinh(Float(0.0))._value == 0.0
    assert Math.cosh(Float(0.0))._value == 1.0
    assert Math.tanh(Float(0.0))._value == 0.0


def test_sinh_returns_poop_float() -> None:
    assert isinstance(Math.sinh(Float(1.0)), Float)


def test_asinh_acosh_atanh() -> None:
    assert Math.asinh(Float(0.0))._value == 0.0
    assert Math.acosh(Float(1.0))._value == 0.0
    assert Math.atanh(Float(0.0))._value == 0.0


# --- Exp / log / power ---


def test_exp_family() -> None:
    assert Math.exp(Float(0.0))._value == 1.0
    assert Math.expm1(Float(0.0))._value == 0.0
    assert Math.exp2(Float(3.0))._value == 8.0


def test_log_default_base_natural() -> None:
    assert Math.log(Float(_math.e))._value == 1.0
    assert isinstance(Math.log(Float(_math.e)), Float)


def test_log_with_explicit_base() -> None:
    assert Math.log(Float(8.0), Float(2.0))._value == 3.0


def test_log2_log10_log1p() -> None:
    assert Math.log2(Float(8.0))._value == 3.0
    assert Math.log10(Float(100.0))._value == 2.0
    assert Math.log1p(Float(0.0))._value == 0.0


def test_cbrt() -> None:
    assert Math.cbrt(Float(8.0))._value == 2.0
    assert Math.cbrt(Float(64.0))._value == 4.0


def test_pow_returns_float() -> None:
    result = Math.pow(Float(2.0), Float(10.0))
    assert isinstance(result, Float)
    assert result._value == 1024.0
