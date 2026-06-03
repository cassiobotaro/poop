import math
from typing import TYPE_CHECKING, ClassVar

from poop.types._unwrap import _unwrap
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import false, to_boolean, true
from poop.types.complex import Complex
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.int import Int
    from poop.types.none import NoneClass
    from poop.types.string import Str
    from poop.types.tuple import Tuple

_float = float  # alias to avoid shadowing by Float.float() method
_int = int  # alias to avoid shadowing by annotations


class Float(_ValueEqMixin, Object):
    __slots__ = ("_value",)
    _eq_attr: ClassVar[str] = "_value"

    def __init__(self, value: _float | Float) -> None:
        self._value = value._value if isinstance(value, Float) else value

    def negated(self) -> Float:
        return Float(-self._value)

    def max(self, other: Float) -> Float:
        return self if self._value >= other._value else other

    def min(self, other: Float) -> Float:
        return self if self._value <= other._value else other

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
        return cls(_float.fromhex(s._value))

    @property
    def real(self) -> Float:
        return self

    @property
    def imag(self) -> Float:
        return Float(0.0)

    def __abs__(self) -> Float:
        return Float(abs(self._value))

    def abs(self) -> Float:
        return self.__abs__()

    def __add__(self, other: Float | Complex) -> Float:
        if isinstance(other, Complex):
            return NotImplemented
        return Float(self._value + other._value)

    def __sub__(self, other: Float | Complex) -> Float:
        if isinstance(other, Complex):
            return NotImplemented
        return Float(self._value - other._value)

    def __mul__(self, other: Float | Complex) -> Float:
        if isinstance(other, Complex):
            return NotImplemented
        return Float(self._value * other._value)

    def __truediv__(self, other: Float | Complex) -> Float:
        if isinstance(other, Complex):
            return NotImplemented
        return Float(self._value / other._value)

    def __floordiv__(self, other: Float) -> Float:
        return Float(self._value // other._value)

    def __mod__(self, other: Float) -> Float:
        return Float(self._value % other._value)

    def __pow__(self, other: Float | Complex) -> Float:
        if isinstance(other, Complex):
            return NotImplemented
        return Float(self._value**other._value)

    def pow(self, other: Float) -> Float:
        return self.__pow__(other)

    def __divmod__(self, other: Float) -> Tuple:
        from poop.types.tuple import Tuple

        q, r = divmod(self._value, other._value)
        return Tuple(Float(q), Float(r))

    def divmod(self, other: Float) -> Tuple:
        return self.__divmod__(other)

    def __ceil__(self) -> Int:
        from poop.types.int import Int

        return Int(math.ceil(self._value))

    def __floor__(self) -> Int:
        from poop.types.int import Int

        return Int(math.floor(self._value))

    def __trunc__(self) -> Int:
        from poop.types.int import Int

        return Int(math.trunc(self._value))

    def __round__(self, ndigits: Int | NoneClass | None = None) -> Int | Float:
        from poop.types.int import Int

        n = _unwrap(ndigits, None)
        result = round(self._value, n)
        return Int(result) if isinstance(result, _int) else Float(result)

    def round(self, ndigits: Int | NoneClass | None = None) -> Int | Float:
        return self.__round__(ndigits)

    def __int__(self) -> _int:
        return _int(self._value)

    def __lt__(self, other: Float) -> Boolean:
        return to_boolean(self._value < other._value)

    def __le__(self, other: Float) -> Boolean:
        return to_boolean(self._value <= other._value)

    def __gt__(self, other: Float) -> Boolean:
        return to_boolean(self._value > other._value)

    def __ge__(self, other: Float) -> Boolean:
        return to_boolean(self._value >= other._value)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.int import Int as _Int

        if isinstance(other, Float | _Int):
            return to_boolean(self._value == other._value)
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.int import Int as _Int

        if isinstance(other, Float | _Int):
            return false if self._value == other._value else true
        return true

    def __hash__(self) -> _int:
        return hash(self._value)

    def __float__(self) -> _float:
        return self._value

    def __bool__(self) -> bool:
        return self._value != 0.0

    def __str__(self) -> str:
        return str(self._value)

    __repr__ = __str__


Float.__module__ = "builtins"
Float.__name__ = "float"
