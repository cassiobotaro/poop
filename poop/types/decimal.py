from __future__ import annotations

import decimal as _decimal
from types import TracebackType
from typing import Any, ClassVar

from poop.types._impl_wrapper import _ImplWrapperMixin
from poop.types._unwrap import _unwrap
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import Boolean, false, true
from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


def _to_decimal(value: Decimal | Int | Float | Str | Tuple) -> _decimal.Decimal:
    if isinstance(value, Decimal):
        return value._impl
    if isinstance(value, Tuple):
        sign: Any = value.at(Int(0))
        digits: Any = value.at(Int(1))
        exponent: Any = value.at(Int(2))
        return _decimal.Decimal(
            (sign._value, tuple(d._value for d in digits), exponent._value)
        )
    return _decimal.Decimal(value._value)


class Decimal(_ImplWrapperMixin, _ValueEqMixin, Object):
    """Wraps Python's `decimal.Decimal` — arbitrary-precision decimal
    arithmetic."""

    __slots__ = ("_impl",)
    _eq_attr: ClassVar[str] = "_impl"

    def __init__(self, value: Decimal | Int | Float | Str | Tuple) -> None:
        self._impl = _to_decimal(value)

    def __add__(self, other: Decimal) -> Decimal:
        return Decimal._from_impl(self._impl + other._impl)

    def __sub__(self, other: Decimal) -> Decimal:
        return Decimal._from_impl(self._impl - other._impl)

    def __mul__(self, other: Decimal) -> Decimal:
        return Decimal._from_impl(self._impl * other._impl)

    def __truediv__(self, other: Decimal) -> Decimal:
        return Decimal._from_impl(self._impl / other._impl)

    def __floordiv__(self, other: Decimal) -> Decimal:
        return Decimal._from_impl(self._impl // other._impl)

    def __mod__(self, other: Decimal) -> Decimal:
        return Decimal._from_impl(self._impl % other._impl)

    def __pow__(self, other: Decimal) -> Decimal:
        return Decimal._from_impl(self._impl**other._impl)

    def __neg__(self) -> Decimal:
        return Decimal._from_impl(-self._impl)

    def __pos__(self) -> Decimal:
        return Decimal._from_impl(+self._impl)

    def __abs__(self) -> Decimal:
        return Decimal._from_impl(abs(self._impl))

    def __hash__(self) -> int:
        return hash(self._impl)

    def __lt__(self, other: Decimal) -> Boolean:
        return true if self._impl < other._impl else false

    def __le__(self, other: Decimal) -> Boolean:
        return true if self._impl <= other._impl else false

    def __gt__(self, other: Decimal) -> Boolean:
        return true if self._impl > other._impl else false

    def __ge__(self, other: Decimal) -> Boolean:
        return true if self._impl >= other._impl else false

    def quantize(
        self, exp: Decimal, rounding: Str | NoneClass | None = None
    ) -> Decimal:
        r = _unwrap(rounding, None)
        return Decimal._from_impl(self._impl.quantize(exp._impl, rounding=r))

    def normalize(self) -> Decimal:
        return Decimal._from_impl(self._impl.normalize())

    def adjusted(self) -> Int:
        return Int(self._impl.adjusted())

    def as_tuple(self) -> Tuple:
        sign, digits, exponent = self._impl.as_tuple()
        digits_tuple = Tuple(*[Int(d) for d in digits])
        exp: Any = Str(exponent) if isinstance(exponent, str) else Int(exponent)
        return Tuple(Int(sign), digits_tuple, exp)

    def as_integer_ratio(self) -> Tuple:
        n, d = self._impl.as_integer_ratio()
        return Tuple(Int(n), Int(d))

    def is_finite(self) -> Boolean:
        return true if self._impl.is_finite() else false

    def is_infinite(self) -> Boolean:
        return true if self._impl.is_infinite() else false

    def is_nan(self) -> Boolean:
        return true if self._impl.is_nan() else false

    def is_signed(self) -> Boolean:
        return true if self._impl.is_signed() else false

    def is_zero(self) -> Boolean:
        return true if self._impl.is_zero() else false

    def sqrt(self) -> Decimal:
        return Decimal._from_impl(self._impl.sqrt())

    def ln(self) -> Decimal:
        return Decimal._from_impl(self._impl.ln())

    def log10(self) -> Decimal:
        return Decimal._from_impl(self._impl.log10())

    def exp(self) -> Decimal:
        return Decimal._from_impl(self._impl.exp())

    def to_integral_value(self, rounding: Str | NoneClass | None = None) -> Decimal:
        r = _unwrap(rounding, None)
        return Decimal._from_impl(self._impl.to_integral_value(rounding=r))

    def copy_abs(self) -> Decimal:
        return Decimal._from_impl(self._impl.copy_abs())

    def copy_negate(self) -> Decimal:
        return Decimal._from_impl(-self._impl)

    def compare(self, other: Decimal) -> Decimal:
        return Decimal._from_impl(self._impl.compare(other._impl))

    def __str__(self) -> str:
        return str(self._impl)


class Context:
    """Wraps Python's `decimal.Context` — arithmetic precision, rounding,
    traps, and flags."""

    __slots__ = ("_impl",)

    def __init__(self, impl: _decimal.Context | None = None) -> None:
        self._impl = impl if impl is not None else _decimal.getcontext()

    @property
    def prec(self) -> Int:
        return Int(self._impl.prec)

    @property
    def rounding(self) -> Str:
        return Str(self._impl.rounding)

    def create_decimal(self, value: Decimal | Int | Float | Str | Tuple) -> Decimal:
        raw = _to_decimal(value)
        return Decimal._from_impl(self._impl.create_decimal(raw))


class _LocalContextWrapper:
    """A POOP-friendly with-context wrapper around
    `decimal.localcontext()`."""

    __slots__ = ("_cm", "_ctx")

    def __init__(self, ctx: Context | NoneClass | None = None) -> None:
        from poop.types._unwrap import _is_absent

        impl = None if _is_absent(ctx) else ctx._impl  # ty: ignore[unresolved-attribute]
        self._cm = _decimal.localcontext(impl)
        self._ctx: Context | None = None

    def __enter__(self) -> Context:
        self._ctx = Context(self._cm.__enter__())
        return self._ctx

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Any:
        return self._cm.__exit__(exc_type, exc_value, traceback)


class Decimal_:
    """Namespace mirroring Python's `decimal` module."""

    Decimal: ClassVar[type[Decimal]] = Decimal

    # Rounding constants — Str (mirroring Python's str ROUND_* names).
    ROUND_UP: ClassVar[Str] = Str(_decimal.ROUND_UP)
    ROUND_DOWN: ClassVar[Str] = Str(_decimal.ROUND_DOWN)
    ROUND_HALF_UP: ClassVar[Str] = Str(_decimal.ROUND_HALF_UP)
    ROUND_HALF_DOWN: ClassVar[Str] = Str(_decimal.ROUND_HALF_DOWN)
    ROUND_HALF_EVEN: ClassVar[Str] = Str(_decimal.ROUND_HALF_EVEN)
    ROUND_CEILING: ClassVar[Str] = Str(_decimal.ROUND_CEILING)
    ROUND_FLOOR: ClassVar[Str] = Str(_decimal.ROUND_FLOOR)
    ROUND_05UP: ClassVar[Str] = Str(_decimal.ROUND_05UP)

    # Signal/exception classes — exposed raw for use with Try.except_.
    DecimalException: ClassVar[type[Exception]] = _decimal.DecimalException
    InvalidOperation: ClassVar[type[Exception]] = _decimal.InvalidOperation
    ConversionSyntax: ClassVar[type[Exception]] = _decimal.ConversionSyntax
    DivisionByZero: ClassVar[type[Exception]] = _decimal.DivisionByZero
    DivisionImpossible: ClassVar[type[Exception]] = _decimal.DivisionImpossible
    DivisionUndefined: ClassVar[type[Exception]] = _decimal.DivisionUndefined
    InvalidContext: ClassVar[type[Exception]] = _decimal.InvalidContext
    Overflow: ClassVar[type[Exception]] = _decimal.Overflow
    Underflow: ClassVar[type[Exception]] = _decimal.Underflow
    Inexact: ClassVar[type[Exception]] = _decimal.Inexact
    Rounded: ClassVar[type[Exception]] = _decimal.Rounded
    Subnormal: ClassVar[type[Exception]] = _decimal.Subnormal
    Clamped: ClassVar[type[Exception]] = _decimal.Clamped
    FloatOperation: ClassVar[type[Exception]] = _decimal.FloatOperation

    # Context profiles + precision limits.
    BasicContext: ClassVar[Context] = Context(_decimal.BasicContext)
    ExtendedContext: ClassVar[Context] = Context(_decimal.ExtendedContext)
    DefaultContext: ClassVar[Context] = Context(_decimal.DefaultContext)
    MAX_PREC: ClassVar[Int] = Int(_decimal.MAX_PREC)
    MAX_EMAX: ClassVar[Int] = Int(_decimal.MAX_EMAX)
    MIN_EMIN: ClassVar[Int] = Int(_decimal.MIN_EMIN)
    MIN_ETINY: ClassVar[Int] = Int(_decimal.MIN_ETINY)
    HAVE_THREADS: ClassVar[Boolean] = true if _decimal.HAVE_THREADS else false
    HAVE_CONTEXTVAR: ClassVar[Boolean] = true if _decimal.HAVE_CONTEXTVAR else false

    @staticmethod
    def getcontext() -> Context:
        return Context(_decimal.getcontext())

    @staticmethod
    def setcontext(context: Context, /) -> NoneClass:
        _decimal.setcontext(context._impl)
        return none

    @staticmethod
    def localcontext(ctx: Context | NoneClass | None = None) -> _LocalContextWrapper:
        return _LocalContextWrapper(ctx)
