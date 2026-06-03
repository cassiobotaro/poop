from typing import TYPE_CHECKING, ClassVar, Literal, cast

from poop.types._unwrap import _unwrap
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import false, to_boolean, true
from poop.types.complex import Complex
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.bytes import Bytes
    from poop.types.float import Float
    from poop.types.none import NoneClass
    from poop.types.string import Str
    from poop.types.tuple import Tuple

_int = int  # alias to avoid shadowing by Int.int() method


class Int(_ValueEqMixin, Object):
    __slots__ = ("_value",)
    _eq_attr: ClassVar[str] = "_value"

    def __init__(self, value: _int | Int) -> None:
        self._value = value._value if isinstance(value, Int) else value

    def negated(self) -> Int:
        return Int(-self._value)

    def bit_invert(self) -> Int:
        return Int(~self._value)

    def max(self, other: Int) -> Int:
        return self if self._value >= other._value else other

    def min(self, other: Int) -> Int:
        return self if self._value <= other._value else other

    def bit_count(self) -> Int:
        return Int(self._value.bit_count())

    def bit_length(self) -> Int:
        return Int(self._value.bit_length())

    def is_integer(self) -> Boolean:
        return true

    @property
    def real(self) -> Int:
        return self

    @property
    def imag(self) -> Int:
        return Int(0)

    @property
    def numerator(self) -> Int:
        return self

    @property
    def denominator(self) -> Int:
        return Int(1)

    def conjugate(self) -> Int:
        return self

    def as_integer_ratio(self) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(self, Int(1))

    def to_bytes(self, length: Int, byteorder: Str) -> Bytes:
        from poop.types.bytes import Bytes

        return Bytes(
            self._value.to_bytes(
                length._value, cast(Literal["little", "big"], byteorder._value)
            )
        )

    @classmethod
    def from_bytes(cls, b: Bytes, byteorder: Str) -> Int:
        return cls(
            _int.from_bytes(b._value, cast(Literal["little", "big"], byteorder._value))
        )

    def __abs__(self) -> Int:
        return Int(abs(self._value))

    def abs(self) -> Int:
        return self.__abs__()

    def __add__(self, other: Int | Float | Complex) -> Int | Float:
        from poop.types.float import Float as _Float

        if isinstance(other, Complex):
            return NotImplemented
        if isinstance(other, _Float):
            return _Float(self._value + other._value)
        return Int(self._value + other._value)

    def __sub__(self, other: Int | Float | Complex) -> Int | Float:
        from poop.types.float import Float as _Float

        if isinstance(other, Complex):
            return NotImplemented
        if isinstance(other, _Float):
            return _Float(self._value - other._value)
        return Int(self._value - other._value)

    def __mul__(self, other: Int | Float | Complex) -> Int | Float:
        from poop.types.float import Float as _Float

        if isinstance(other, Complex):
            return NotImplemented
        if isinstance(other, _Float):
            return _Float(self._value * other._value)
        return Int(self._value * other._value)

    def __truediv__(self, other: Int | Complex) -> Float:
        from poop.types.float import Float

        if isinstance(other, Complex):
            return NotImplemented
        return Float(self._value / other._value)

    def __floordiv__(self, other: Int | Float) -> Int | Float:
        from poop.types.float import Float as _Float

        if isinstance(other, _Float):
            return _Float(self._value // other._value)
        return Int(self._value // other._value)

    def __mod__(self, other: Int | Float) -> Int | Float:
        from poop.types.float import Float as _Float

        if isinstance(other, _Float):
            return _Float(self._value % other._value)
        return Int(self._value % other._value)

    def __pow__(
        self, other: Int | Complex, modulus: Int | NoneClass | None = None
    ) -> Int | Float:
        from poop.types._unwrap import _is_absent
        from poop.types.float import Float

        if isinstance(other, Complex):
            return NotImplemented
        if _is_absent(modulus):
            result = self._value**other._value
            if isinstance(result, float):
                return Float(result)
            return Int(result)
        return Int(pow(self._value, other._value, modulus._value))  # ty: ignore[unresolved-attribute]

    def pow(self, other: Int, modulus: Int | NoneClass | None = None) -> Int | Float:
        return self.__pow__(other, modulus)

    def __divmod__(self, other: Int) -> Tuple:
        from poop.types.tuple import Tuple

        q, r = divmod(self._value, other._value)
        return Tuple(Int(q), Int(r))

    def divmod(self, other: Int) -> Tuple:
        return self.__divmod__(other)

    def __lshift__(self, other: Int) -> Int:
        return Int(self._value << other._value)

    def __rshift__(self, other: Int) -> Int:
        return Int(self._value >> other._value)

    def __and__(self, other: Int) -> Int:
        return Int(self._value & other._value)

    def __or__(self, other: Int) -> Int:
        return Int(self._value | other._value)

    def __xor__(self, other: Int) -> Int:
        return Int(self._value ^ other._value)

    def __ceil__(self) -> Int:
        return self

    def __floor__(self) -> Int:
        return self

    def __trunc__(self) -> Int:
        return self

    def __round__(self, ndigits: Int | NoneClass | None = None) -> Int:

        n = _unwrap(ndigits, None)
        return Int(round(self._value, n))

    def round(self, ndigits: Int | NoneClass | None = None) -> Int:
        return self.__round__(ndigits)

    def __lt__(self, other: Int) -> Boolean:
        return to_boolean(self._value < other._value)

    def __le__(self, other: Int) -> Boolean:
        return to_boolean(self._value <= other._value)

    def __gt__(self, other: Int) -> Boolean:
        return to_boolean(self._value > other._value)

    def __ge__(self, other: Int) -> Boolean:
        return to_boolean(self._value >= other._value)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.float import Float as _Float

        if isinstance(other, Int | _Float):
            return to_boolean(self._value == other._value)
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.float import Float as _Float

        if isinstance(other, Int | _Float):
            return false if self._value == other._value else true
        return true

    def __hash__(self) -> _int:
        return hash(self._value)

    def bin(self) -> Str:
        from poop.types.string import Str

        return Str(bin(self._value))

    def hex(self) -> Str:
        from poop.types.string import Str

        return Str(hex(self._value))

    def oct(self) -> Str:
        from poop.types.string import Str

        return Str(oct(self._value))

    def chr(self) -> Str:
        from poop.types.string import Str

        return Str(chr(self._value))

    def __int__(self) -> _int:
        return self._value

    def __bool__(self) -> bool:
        return self._value != 0

    def __str__(self) -> str:
        return str(self._value)

    __repr__ = __str__


Int.__module__ = "builtins"
Int.__name__ = "int"
