import builtins as _builtins
import math
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, cast

from poop.types._alias import wrapped_instance
from poop.types._cloak import cloak
from poop.types._message import binary_refusal
from poop.types._minmax import _MISSING, _minmax
from poop.types._numeric_compare import (
    _NOT_NUMERIC,
    _num_value,
    _NumericCompareMixin,
)
from poop.types._pow import reflected_pow
from poop.types._unwrap import _faithful, _unwrap
from poop.types.boolean import to_boolean
from poop.types.complex import Complex
from poop.types.exceptions import MIRRORS
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.int import Int
    from poop.types.none import NoneClass
    from poop.types.string import Str
    from poop.types.tuple import Tuple

_float = float  # alias to avoid shadowing by Float.float() method
_int = int  # alias to avoid shadowing by annotations


class Float(_NumericCompareMixin, Object):
    __slots__ = ("_value",)

    def __init__(self, value: _float | Float) -> None:
        self._value = value._value if isinstance(value, Float) else value

    def negated(self) -> Float:
        return Float(-self._value)

    # Same reasoning as `Int.max` / `Int.min`: comparing the operands routes
    # a Boolean through the numeric mixin and a foreign operand to CPython's
    # faithful TypeError, instead of reading `other._value` and leaking it.
    # The cast mirrors typeshed, which types the answer by the receiver even
    # when the winning operand belongs to another rung of the tower.
    # `key` is keyword-only, as CPython spells it: a positional block would be
    # indistinguishable from one more operand, which is how it used to be read.
    def max(
        self,
        *others: Float | Int | Boolean,
        key: Callable[[Any], Any] | NoneClass | None = None,
    ) -> Float:
        return cast(
            "Float", _minmax(_builtins.max, "#max", (self, *others), key, _MISSING)
        )

    def min(
        self,
        *others: Float | Int | Boolean,
        key: Callable[[Any], Any] | NoneClass | None = None,
    ) -> Float:
        return cast(
            "Float", _minmax(_builtins.min, "#min", (self, *others), key, _MISSING)
        )

    def is_integer(self) -> Boolean:
        return to_boolean(self._value.is_integer())

    def as_integer_ratio(self) -> Tuple:
        from poop.types.int import Int
        from poop.types.tuple import Tuple

        n, d = self._value.as_integer_ratio()
        return Tuple(Int(n), Int(d))

    def conjugate(self) -> Float:
        return self

    def hex(self) -> Str:
        from poop.types.string import Str

        return Str(_float(self._value).hex())

    @classmethod
    def fromhex(cls, s: Str) -> Float:
        return wrapped_instance(cls, _float.fromhex(_faithful(s)))

    def real(self) -> Float:
        return self

    def imag(self) -> Float:
        return Float(0.0)

    def __abs__(self) -> Float:
        return Float(abs(self._value))

    def abs(self) -> Float:
        return self.__abs__()

    def __add__(self, other: object) -> Float:
        from poop.types.int import Int

        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__radd__ run
        return Float(self._value + other._value)

    def __sub__(self, other: object) -> Float:
        from poop.types.int import Int

        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__rsub__ run
        return Float(self._value - other._value)

    def __mul__(self, other: object) -> Float:
        from poop.types.int import Int

        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__rmul__ run
        return Float(self._value * other._value)

    def __truediv__(self, other: object) -> Float:
        from poop.types.int import Int

        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__rtruediv__ run
        return Float(self._value / other._value)

    def __floordiv__(self, other: object) -> Float:
        from poop.types.int import Int

        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__rfloordiv__ run
        return Float(self._value // other._value)

    def __mod__(self, other: object) -> Float:
        from poop.types.int import Int

        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__rmod__ run
        return Float(self._value % other._value)

    def __pow__(self, other: object) -> Float | Complex:
        from poop.types.int import Int

        if isinstance(other, Complex):
            return NotImplemented
        if not isinstance(other, Int | Float):
            return NotImplemented  # let other.__rpow__ run (e.g. Boolean)
        result = self._value**other._value
        if isinstance(result, complex):
            return Complex(result)
        return Float(result)

    def pow(
        self, other: object, modulus: Int | NoneClass | None = None
    ) -> Float | Complex:
        # The third slot exists so the message has the same shape on every
        # rung: without it `(2.0).pow(3, 5)` answered CPython's *signature*
        # error — `float.pow() takes 2 positional arguments but 3 were given`,
        # naming a message as a call — while `(2).pow(3.0, 5)` one line away
        # answered the operation. CPython refuses the float form too, but as
        # an operation, so the refusal is `Int.__pow__`'s own sentence.
        #
        # In `pow`, not `__pow__`: the operator never carries a third operand
        # (`a ** b % m` is two operations, and the builtin `pow` is banned).
        from poop.types._unwrap import _is_absent

        if not _is_absent(modulus):
            raise MIRRORS["TypeError"](
                "pow's modulus is only defined when both operands are ints"
            )
        # See `Int.pow`: `__pow__` answers `NotImplemented` for a `Complex` so
        # the operator can fall through to `Complex.__rpow__`, and the message
        # has to complete the same protocol or it refuses what `**` computes.
        result = self.__pow__(other)
        if result is NotImplemented:
            result = reflected_pow(self, other, None)
        if result is NotImplemented:
            raise MIRRORS["TypeError"](
                binary_refusal("float", "pow", type(other).__name__)
            )
        return result

    def __divmod__(self, other: object) -> Tuple:
        from poop.types.tuple import Tuple

        v = _num_value(other)
        if v is _NOT_NUMERIC:
            return NotImplemented  # let other.__rdivmod__ run / faithful TypeError
        q, r = divmod(self._value, v)
        return Tuple(Float(q), Float(r))

    def divmod(self, other: object) -> Tuple:
        result = self.__divmod__(other)
        if result is NotImplemented:
            raise MIRRORS["TypeError"](
                binary_refusal("float", "divmod", type(other).__name__)
            )
        return result

    def __ceil__(self) -> Int:
        from poop.types.int import Int

        return Int(math.ceil(self._value))

    def ceil(self) -> Int:
        return self.__ceil__()

    def __floor__(self) -> Int:
        from poop.types.int import Int

        return Int(math.floor(self._value))

    def floor(self) -> Int:
        return self.__floor__()

    def __trunc__(self) -> Int:
        from poop.types.int import Int

        return Int(math.trunc(self._value))

    def trunc(self) -> Int:
        return self.__trunc__()

    def __round__(self, ndigits: Int | NoneClass | None = None) -> Int | Float:
        from poop.types.int import Int

        n = _unwrap(ndigits, None)
        result = round(self._value, n)
        return Int(result) if isinstance(result, _int) else Float(result)

    def round(self, ndigits: Int | NoneClass | None = None) -> Int | Float:
        return self.__round__(ndigits)

    def __int__(self) -> _int:
        return _int(self._value)

    # Ordering (__lt__/__le__/__gt__/__ge__) and equality (__eq__/__ne__)
    # across the numeric tower live in _NumericCompareMixin, driven by
    # _order_value() (Float's raw value is self._value, the default).

    def __hash__(self) -> _int:
        return hash(self._value)

    def __float__(self) -> _float:
        return self._value

    def __bool__(self) -> bool:
        return self._value != 0.0

    def __str__(self) -> str:
        return str(self._value)

    __repr__ = __str__


cloak(Float, "float")
