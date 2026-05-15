import math as _math
from typing import TYPE_CHECKING, ClassVar

from poop.types.float import Float
from poop.types.int import Int

if TYPE_CHECKING:
    from poop.types.tuple import Tuple


class Math:
    """Namespace mirroring Python's `math` module.

    Every public function in `math.*` is exposed as a `@staticmethod`
    with the same name, parameter order, defaults, and return types.
    Constants are recased to UPPER_SNAKE_CASE for consistency with
    `Uuid.NAMESPACE_DNS`, `Secrets.DEFAULT_ENTROPY`, etc.
    """

    PI: ClassVar[Float] = Float(_math.pi)
    E: ClassVar[Float] = Float(_math.e)
    TAU: ClassVar[Float] = Float(_math.tau)
    INF: ClassVar[Float] = Float(_math.inf)
    NAN: ClassVar[Float] = Float(_math.nan)

    # Number theory ------------------------------------------------

    @staticmethod
    def factorial(n: Int) -> Int:
        return Int(_math.factorial(n._value))

    @staticmethod
    def gcd(*integers: Int) -> Int:
        return Int(_math.gcd(*(n._value for n in integers)))

    @staticmethod
    def lcm(*integers: Int) -> Int:
        return Int(_math.lcm(*(n._value for n in integers)))

    @staticmethod
    def comb(n: Int, k: Int) -> Int:
        return Int(_math.comb(n._value, k._value))

    @staticmethod
    def perm(n: Int, k: Int | None = None) -> Int:
        return Int(_math.perm(n._value, k._value if k is not None else None))

    @staticmethod
    def isqrt(n: Int) -> Int:
        return Int(_math.isqrt(n._value))

    # Trigonometric -----------------------------------------------

    @staticmethod
    def sin(x: Float) -> Float:
        return Float(_math.sin(x._value))

    @staticmethod
    def cos(x: Float) -> Float:
        return Float(_math.cos(x._value))

    @staticmethod
    def tan(x: Float) -> Float:
        return Float(_math.tan(x._value))

    @staticmethod
    def asin(x: Float) -> Float:
        return Float(_math.asin(x._value))

    @staticmethod
    def acos(x: Float) -> Float:
        return Float(_math.acos(x._value))

    @staticmethod
    def atan(x: Float) -> Float:
        return Float(_math.atan(x._value))

    @staticmethod
    def atan2(y: Float, x: Float) -> Float:
        return Float(_math.atan2(y._value, x._value))

    # Hyperbolic --------------------------------------------------

    @staticmethod
    def sinh(x: Float) -> Float:
        return Float(_math.sinh(x._value))

    @staticmethod
    def cosh(x: Float) -> Float:
        return Float(_math.cosh(x._value))

    @staticmethod
    def tanh(x: Float) -> Float:
        return Float(_math.tanh(x._value))

    @staticmethod
    def asinh(x: Float) -> Float:
        return Float(_math.asinh(x._value))

    @staticmethod
    def acosh(x: Float) -> Float:
        return Float(_math.acosh(x._value))

    @staticmethod
    def atanh(x: Float) -> Float:
        return Float(_math.atanh(x._value))

    # Power & exponential -----------------------------------------

    @staticmethod
    def exp(x: Float) -> Float:
        return Float(_math.exp(x._value))

    @staticmethod
    def expm1(x: Float) -> Float:
        return Float(_math.expm1(x._value))

    @staticmethod
    def exp2(x: Float) -> Float:
        return Float(_math.exp2(x._value))

    @staticmethod
    def log(x: Float, base: Float = Float(_math.e)) -> Float:
        return Float(_math.log(x._value, base._value))

    @staticmethod
    def log2(x: Float) -> Float:
        return Float(_math.log2(x._value))

    @staticmethod
    def log10(x: Float) -> Float:
        return Float(_math.log10(x._value))

    @staticmethod
    def log1p(x: Float) -> Float:
        return Float(_math.log1p(x._value))

    @staticmethod
    def sqrt(x: Float) -> Float:
        return Float(_math.sqrt(x._value))

    @staticmethod
    def cbrt(x: Float) -> Float:
        return Float(_math.cbrt(x._value))

    @staticmethod
    def pow(x: Float, y: Float) -> Float:
        return Float(_math.pow(x._value, y._value))

    # Rounding & float decomposition ------------------------------

    @staticmethod
    def floor(x: Float) -> Int:
        return Int(_math.floor(x._value))

    @staticmethod
    def ceil(x: Float) -> Int:
        return Int(_math.ceil(x._value))

    @staticmethod
    def trunc(x: Float) -> Int:
        return Int(_math.trunc(x._value))

    @staticmethod
    def modf(x: Float) -> Tuple:
        from poop.types.tuple import Tuple

        frac, integ = _math.modf(x._value)
        return Tuple(Float(frac), Float(integ))

    @staticmethod
    def frexp(x: Float) -> Tuple:
        from poop.types.tuple import Tuple

        mantissa, exponent = _math.frexp(x._value)
        return Tuple(Float(mantissa), Int(exponent))

    @staticmethod
    def ldexp(x: Float, i: Int) -> Float:
        return Float(_math.ldexp(x._value, i._value))

    # Angular conversion ------------------------------------------

    @staticmethod
    def degrees(x: Float) -> Float:
        return Float(_math.degrees(x._value))

    @staticmethod
    def radians(x: Float) -> Float:
        return Float(_math.radians(x._value))
