from typing import TYPE_CHECKING, Literal, cast

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.bytes import Bytes
    from poop.types.float import Float
    from poop.types.range import Range
    from poop.types.string import Str
    from poop.types.tuple import Tuple

_int = int  # alias to avoid shadowing by Int.int() method


class Int(Object):
    __slots__ = ("_value",)

    def __init__(self, value: _int) -> None:
        self._value = value

    def negated(self) -> Int:
        return Int(-self._value)

    def bit_invert(self) -> Int:
        return Int(~self._value)

    def to_(self, limit: Int) -> Range:
        from poop.types.range import Range

        return Range(self, limit)

    def to_by_(self, limit: Int, step: Int) -> Range:
        from poop.types.range import Range

        return Range(self, limit, step)

    def max(self, other: Int) -> Int:
        return self if self._value >= other._value else other

    def min(self, other: Int) -> Int:
        return self if self._value <= other._value else other

    def bit_count(self) -> Int:
        return Int(self._value.bit_count())

    def bit_length(self) -> Int:
        return Int(self._value.bit_length())

    def is_integer(self) -> Boolean:
        from poop.types.boolean import true

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

    def int(self) -> Int:
        return self

    def float(self) -> Float:
        from poop.types.float import Float

        return Float(float(self._value))

    def __abs__(self) -> Int:
        return Int(abs(self._value))

    def abs(self) -> Int:
        return self.__abs__()

    def __add__(self, other: Int) -> Int:
        return Int(self._value + other._value)

    def __sub__(self, other: Int) -> Int:
        return Int(self._value - other._value)

    def __mul__(self, other: Int) -> Int:
        return Int(self._value * other._value)

    def __truediv__(self, other: Int) -> Float:
        from poop.types.float import Float

        return Float(self._value / other._value)

    def __floordiv__(self, other: Int) -> Int:
        return Int(self._value // other._value)

    def __mod__(self, other: Int) -> Int:
        return Int(self._value % other._value)

    def __pow__(self, other: Int) -> Int:
        return Int(self._value**other._value)

    def pow(self, other: Int) -> Int:
        return self.__pow__(other)

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

    def ceil(self) -> Int:
        return self.__ceil__()

    def __floor__(self) -> Int:
        return self

    def floor(self) -> Int:
        return self.__floor__()

    def __trunc__(self) -> Int:
        return self

    def trunc(self) -> Int:
        return self.__trunc__()

    def __round__(self, ndigits: _int | None = None) -> Int:
        return Int(round(self._value, ndigits))

    def round(self, ndigits: _int | None = None) -> Int:
        return self.__round__(ndigits)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Int):
            return true if self._value == other._value else false
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Int):
            return false if self._value == other._value else true
        return true

    def __lt__(self, other: Int) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value < other._value else false

    def __le__(self, other: Int) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value <= other._value else false

    def __gt__(self, other: Int) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value > other._value else false

    def __ge__(self, other: Int) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value >= other._value else false

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
