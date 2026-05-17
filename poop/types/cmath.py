import cmath as _cmath
from typing import TYPE_CHECKING, ClassVar

from poop.types.boolean import false, true
from poop.types.complex import Complex
from poop.types.float import Float

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.tuple import Tuple


class CMath:
    """Namespace mirroring Python's `cmath` module.

    Every public function in `cmath.*` is exposed as a `@staticmethod`
    with the same name, parameter order, defaults, and return types.
    Constants follow the source module's case verbatim — lowercase
    `pi`, `e`, `tau`, `inf`, `nan`, `infj`, `nanj` because that is
    how `cmath` ships them in Python.

    Predicates (`isfinite`/`isinf`/`isnan`) are defined on the whole
    Complex (true iff both real and imag satisfy the predicate),
    matching CPython's `cmath.*` semantics. They are deliberately
    separate from `math.isfinite`/`isinf`/`isnan` (which take Float),
    mirroring Python's two-namespace split.
    """

    pi: ClassVar[Float] = Float(_cmath.pi)
    e: ClassVar[Float] = Float(_cmath.e)
    tau: ClassVar[Float] = Float(_cmath.tau)
    inf: ClassVar[Float] = Float(_cmath.inf)
    nan: ClassVar[Float] = Float(_cmath.nan)
    infj: ClassVar[Complex] = Complex(_cmath.infj)
    nanj: ClassVar[Complex] = Complex(_cmath.nanj)

    # Power & logarithmic -----------------------------------------

    @staticmethod
    def sqrt(x: Complex) -> Complex:
        return Complex(_cmath.sqrt(x._value))

    @staticmethod
    def exp(x: Complex) -> Complex:
        return Complex(_cmath.exp(x._value))

    @staticmethod
    def log(x: Complex, base: Complex | None = None) -> Complex:
        if base is None:
            return Complex(_cmath.log(x._value))
        return Complex(_cmath.log(x._value, base._value))

    @staticmethod
    def log10(x: Complex) -> Complex:
        return Complex(_cmath.log10(x._value))

    # Trigonometric -----------------------------------------------

    @staticmethod
    def sin(x: Complex) -> Complex:
        return Complex(_cmath.sin(x._value))

    @staticmethod
    def cos(x: Complex) -> Complex:
        return Complex(_cmath.cos(x._value))

    @staticmethod
    def tan(x: Complex) -> Complex:
        return Complex(_cmath.tan(x._value))

    @staticmethod
    def asin(x: Complex) -> Complex:
        return Complex(_cmath.asin(x._value))

    @staticmethod
    def acos(x: Complex) -> Complex:
        return Complex(_cmath.acos(x._value))

    @staticmethod
    def atan(x: Complex) -> Complex:
        return Complex(_cmath.atan(x._value))

    # Hyperbolic --------------------------------------------------

    @staticmethod
    def sinh(x: Complex) -> Complex:
        return Complex(_cmath.sinh(x._value))

    @staticmethod
    def cosh(x: Complex) -> Complex:
        return Complex(_cmath.cosh(x._value))

    @staticmethod
    def tanh(x: Complex) -> Complex:
        return Complex(_cmath.tanh(x._value))

    @staticmethod
    def asinh(x: Complex) -> Complex:
        return Complex(_cmath.asinh(x._value))

    @staticmethod
    def acosh(x: Complex) -> Complex:
        return Complex(_cmath.acosh(x._value))

    @staticmethod
    def atanh(x: Complex) -> Complex:
        return Complex(_cmath.atanh(x._value))

    # Polar / rectangular conversion ------------------------------

    @staticmethod
    def phase(x: Complex) -> Float:
        return Float(_cmath.phase(x._value))

    @staticmethod
    def polar(x: Complex) -> Tuple:
        from poop.types.tuple import Tuple

        r, phi = _cmath.polar(x._value)
        return Tuple(Float(r), Float(phi))

    @staticmethod
    def rect(r: Float, phi: Float) -> Complex:
        return Complex(_cmath.rect(r._value, phi._value))

    # Predicates --------------------------------------------------

    @staticmethod
    def isfinite(x: Complex) -> Boolean:
        return true if _cmath.isfinite(x._value) else false

    @staticmethod
    def isinf(x: Complex) -> Boolean:
        return true if _cmath.isinf(x._value) else false

    @staticmethod
    def isnan(x: Complex) -> Boolean:
        return true if _cmath.isnan(x._value) else false

    @staticmethod
    def isclose(
        a: Complex,
        b: Complex,
        *,
        rel_tol: Float = Float(1e-9),
        abs_tol: Float = Float(0.0),
    ) -> Boolean:
        return (
            true
            if _cmath.isclose(
                a._value, b._value, rel_tol=rel_tol._value, abs_tol=abs_tol._value
            )
            else false
        )
