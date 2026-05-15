import math as _math

from poop.interpreter import Interpreter
from poop.types.float import Float
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
