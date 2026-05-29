import cmath as _cmath
from typing import TYPE_CHECKING, ClassVar

from poop.types.boolean import false, to_boolean, true
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.none import NoneClass

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
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
    def sqrt(z: Complex, /) -> Complex:
        return Complex(_cmath.sqrt(z._value))

    @staticmethod
    def exp(z: Complex, /) -> Complex:
        return Complex(_cmath.exp(z._value))

    @staticmethod
    def log(x: Complex, base: Complex | NoneClass | None = None) -> Complex:
        from poop.types._unwrap import _is_absent

        if _is_absent(base):
            return Complex(_cmath.log(x._value))
        return Complex(_cmath.log(x._value, base._value))  # ty: ignore[unresolved-attribute]

    @staticmethod
    def log10(z: Complex, /) -> Complex:
        return Complex(_cmath.log10(z._value))

    # Trigonometric -----------------------------------------------

    @staticmethod
    def sin(z: Complex, /) -> Complex:
        return Complex(_cmath.sin(z._value))

    @staticmethod
    def cos(z: Complex, /) -> Complex:
        return Complex(_cmath.cos(z._value))

    @staticmethod
    def tan(z: Complex, /) -> Complex:
        return Complex(_cmath.tan(z._value))

    @staticmethod
    def asin(z: Complex, /) -> Complex:
        return Complex(_cmath.asin(z._value))

    @staticmethod
    def acos(z: Complex, /) -> Complex:
        return Complex(_cmath.acos(z._value))

    @staticmethod
    def atan(z: Complex, /) -> Complex:
        return Complex(_cmath.atan(z._value))

    # Hyperbolic --------------------------------------------------

    @staticmethod
    def sinh(z: Complex, /) -> Complex:
        return Complex(_cmath.sinh(z._value))

    @staticmethod
    def cosh(z: Complex, /) -> Complex:
        return Complex(_cmath.cosh(z._value))

    @staticmethod
    def tanh(z: Complex, /) -> Complex:
        return Complex(_cmath.tanh(z._value))

    @staticmethod
    def asinh(z: Complex, /) -> Complex:
        return Complex(_cmath.asinh(z._value))

    @staticmethod
    def acosh(z: Complex, /) -> Complex:
        return Complex(_cmath.acosh(z._value))

    @staticmethod
    def atanh(z: Complex, /) -> Complex:
        return Complex(_cmath.atanh(z._value))

    # Polar / rectangular conversion ------------------------------

    @staticmethod
    def phase(z: Complex, /) -> Float:
        return Float(_cmath.phase(z._value))

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
        return to_boolean(_cmath.isfinite(x._value))

    @staticmethod
    def isinf(x: Complex) -> Boolean:
        return to_boolean(_cmath.isinf(x._value))

    @staticmethod
    def isnan(x: Complex) -> Boolean:
        return to_boolean(_cmath.isnan(x._value))

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
