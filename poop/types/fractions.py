from __future__ import annotations

import fractions as _fractions
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._impl_wrapper import _ImplWrapperMixin
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import Boolean, to_boolean
from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import NoneClass
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.decimal import Decimal


def _to_python_num(value: Any) -> Any:
    if isinstance(value, Fraction):
        return value._impl
    if isinstance(value, Int | Float | Str):
        return value._value
    return value


class Fraction(_ImplWrapperMixin, _ValueEqMixin, Object):
    """Wraps Python's `fractions.Fraction` — exact rational arithmetic.

    Constructors mirror CPython:

    - `Fraction(numerator=0, denominator=1)` — both `Int`
    - `Fraction(Str("3/4"))` — string form
    - `Fraction(Str("0.25"))` — decimal string
    - `Fraction(Float(0.5))` — direct from float (exact bit pattern)
    - `Fraction.from_float(f)` / `Fraction.from_decimal(d)` —
      classmethods matching CPython.

    Arithmetic between `Fraction`s returns `Fraction`; mixing with
    `Int` keeps `Fraction`; mixing with `Float` promotes to `Float`.
    """

    __slots__ = ("_impl",)
    _eq_attr: ClassVar[str] = "_impl"

    def __init__(
        self,
        numerator: Int | Float | Str | Fraction | NoneClass | None = None,
        denominator: Int | NoneClass | None = None,
    ) -> None:
        from poop.types._unwrap import _is_absent

        if _is_absent(numerator):
            self._impl = _fractions.Fraction()
        elif not _is_absent(denominator):
            # Two-argument form: both numerator and denominator are Int.
            self._impl = _fractions.Fraction(
                _to_python_num(numerator), _to_python_num(denominator)
            )
        elif isinstance(numerator, Fraction):
            self._impl = numerator._impl
        else:
            self._impl = _fractions.Fraction(_to_python_num(numerator))

    @classmethod
    def from_float(cls, f: Float) -> Fraction:
        return cls._from_impl(_fractions.Fraction.from_float(f._value))

    @classmethod
    def from_decimal(cls, d: Decimal) -> Fraction:
        return cls._from_impl(_fractions.Fraction.from_decimal(d._impl))

    @property
    def numerator(self) -> Int:
        return Int(self._impl.numerator)

    @property
    def denominator(self) -> Int:
        return Int(self._impl.denominator)

    def limit_denominator(
        self, max_denominator: Int | NoneClass | None = None
    ) -> Fraction:
        from poop.types._unwrap import _is_absent

        if _is_absent(max_denominator):
            return Fraction._from_impl(self._impl.limit_denominator())
        return Fraction._from_impl(self._impl.limit_denominator(max_denominator._value))

    def as_integer_ratio(self) -> Tuple:
        n, d = self._impl.as_integer_ratio()
        return Tuple(Int(n), Int(d))

    # Arithmetic -----------------------------------------------------

    def _combine(self, other: Any, op: Any) -> Any:
        if isinstance(other, Fraction):
            return Fraction._from_impl(op(self._impl, other._impl))
        if isinstance(other, Int):
            return Fraction._from_impl(op(self._impl, other._value))
        if isinstance(other, Float):
            return Float(op(float(self._impl), other._value))
        return NotImplemented

    def __add__(self, other: Any) -> Any:
        return self._combine(other, lambda a, b: a + b)

    def __radd__(self, other: Any) -> Any:
        return self._combine(other, lambda a, b: b + a)

    def __sub__(self, other: Any) -> Any:
        return self._combine(other, lambda a, b: a - b)

    def __rsub__(self, other: Any) -> Any:
        return self._combine(other, lambda a, b: b - a)

    def __mul__(self, other: Any) -> Any:
        return self._combine(other, lambda a, b: a * b)

    def __rmul__(self, other: Any) -> Any:
        return self._combine(other, lambda a, b: b * a)

    def __truediv__(self, other: Any) -> Any:
        return self._combine(other, lambda a, b: a / b)

    def __rtruediv__(self, other: Any) -> Any:
        return self._combine(other, lambda a, b: b / a)

    def __floordiv__(self, other: Any) -> Any:
        if isinstance(other, Fraction):
            return Int(self._impl // other._impl)
        if isinstance(other, Int):
            return Int(self._impl // other._value)
        if isinstance(other, Float):
            return Float(float(self._impl) // other._value)
        return NotImplemented

    def __mod__(self, other: Any) -> Any:
        return self._combine(other, lambda a, b: a % b)

    def __pow__(self, other: Any) -> Any:
        if isinstance(other, Int):
            result = self._impl**other._value
            if isinstance(result, _fractions.Fraction):
                return Fraction._from_impl(result)
            return Float(result)
        if isinstance(other, Float):
            return Float(float(self._impl) ** other._value)
        if isinstance(other, Fraction):
            result = self._impl**other._impl
            if isinstance(result, _fractions.Fraction):
                return Fraction._from_impl(result)
            return Float(result)
        return NotImplemented

    def __neg__(self) -> Fraction:
        return Fraction._from_impl(-self._impl)

    def __pos__(self) -> Fraction:
        return Fraction._from_impl(+self._impl)

    def __abs__(self) -> Fraction:
        return Fraction._from_impl(abs(self._impl))

    # Comparison -----------------------------------------------------

    def _cmp(self, other: Any, op: Any) -> Any:
        if isinstance(other, Fraction):
            return to_boolean(op(self._impl, other._impl))
        if isinstance(other, Int):
            return to_boolean(op(self._impl, other._value))
        if isinstance(other, Float):
            return to_boolean(op(float(self._impl), other._value))
        return NotImplemented

    def __lt__(self, other: Any) -> Boolean:
        return self._cmp(other, lambda a, b: a < b)

    def __le__(self, other: Any) -> Boolean:
        return self._cmp(other, lambda a, b: a <= b)

    def __gt__(self, other: Any) -> Boolean:
        return self._cmp(other, lambda a, b: a > b)

    def __ge__(self, other: Any) -> Boolean:
        return self._cmp(other, lambda a, b: a >= b)

    def __hash__(self) -> int:
        return hash(self._impl)

    # String forms ---------------------------------------------------

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class FractionsNamespace:
    """Namespace mirroring Python's `fractions` module.

    `Fraction` is exposed bare (PascalCase) and via `fractions.Fraction`
    — matching the `uuid` / `UUID` and `hmac` / `HMAC` convention.
    """

    Fraction: ClassVar[type[Fraction]] = Fraction
