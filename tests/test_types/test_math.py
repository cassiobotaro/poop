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
