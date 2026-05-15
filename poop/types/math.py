import math as _math
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types.boolean import false, true
from poop.types.float import Float
from poop.types.int import Int

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
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

    # Float utilities ---------------------------------------------

    @staticmethod
    def fabs(x: Float) -> Float:
        return Float(_math.fabs(x._value))

    @staticmethod
    def copysign(x: Float, y: Float) -> Float:
        return Float(_math.copysign(x._value, y._value))

    @staticmethod
    def fmod(x: Float, y: Float) -> Float:
        return Float(_math.fmod(x._value, y._value))

    @staticmethod
    def remainder(x: Float, y: Float) -> Float:
        return Float(_math.remainder(x._value, y._value))

    @staticmethod
    def fma(x: Float, y: Float, z: Float) -> Float:
        return Float(_math.fma(x._value, y._value, z._value))

    @staticmethod
    def ulp(x: Float) -> Float:
        return Float(_math.ulp(x._value))

    @staticmethod
    def nextafter(x: Float, y: Float, *, steps: Int | None = None) -> Float:
        if steps is None:
            return Float(_math.nextafter(x._value, y._value))
        return Float(_math.nextafter(x._value, y._value, steps=steps._value))

    # Predicates --------------------------------------------------

    @staticmethod
    def isfinite(x: Float) -> Boolean:
        return true if _math.isfinite(x._value) else false

    @staticmethod
    def isinf(x: Float) -> Boolean:
        return true if _math.isinf(x._value) else false

    @staticmethod
    def isnan(x: Float) -> Boolean:
        return true if _math.isnan(x._value) else false

    @staticmethod
    def isclose(
        a: Float,
        b: Float,
        *,
        rel_tol: Float = Float(1e-9),
        abs_tol: Float = Float(0.0),
    ) -> Boolean:
        return (
            true
            if _math.isclose(
                a._value, b._value, rel_tol=rel_tol._value, abs_tol=abs_tol._value
            )
            else false
        )

    # Aggregates over iterables -----------------------------------

    @staticmethod
    def fsum(seq: Any) -> Float:
        return Float(_math.fsum(x._value for x in seq))

    @staticmethod
    def prod(iterable: Any, *, start: Int | Float = Int(1)) -> Int | Float:
        result = _math.prod((x._value for x in iterable), start=start._value)
        return Float(result) if isinstance(result, float) else Int(result)

    @staticmethod
    def sumprod(p: Any, q: Any) -> Int | Float:
        result = _math.sumprod((x._value for x in p), (y._value for y in q))
        return Float(result) if isinstance(result, float) else Int(result)

    @staticmethod
    def dist(p: Any, q: Any) -> Float:
        return Float(_math.dist([x._value for x in p], [y._value for y in q]))

    @staticmethod
    def hypot(*coordinates: Int | Float) -> Float:
        return Float(_math.hypot(*(c._value for c in coordinates)))

    # Special functions -------------------------------------------

    @staticmethod
    def erf(x: Float) -> Float:
        return Float(_math.erf(x._value))

    @staticmethod
    def erfc(x: Float) -> Float:
        return Float(_math.erfc(x._value))

    @staticmethod
    def gamma(x: Float) -> Float:
        return Float(_math.gamma(x._value))

    @staticmethod
    def lgamma(x: Float) -> Float:
        return Float(_math.lgamma(x._value))
