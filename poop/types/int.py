from collections.abc import Callable
from typing import TYPE_CHECKING

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.float import Float
    from poop.types.interval import Interval
    from poop.types.string import Str


class Int(Object):
    __slots__ = ("_value",)

    def __init__(self, value: int) -> None:
        self._value = value

    def negated(self) -> Int:
        return Int(-self._value)

    def bit_invert(self) -> Int:
        return Int(~self._value)

    def times_repeat[T](self, block: Callable[[], T]) -> None:
        for _ in range(self._value):
            block()

    def to_(self, limit: Int) -> Interval:
        from poop.types.interval import Interval

        return Interval(self, limit)

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

    def as_float(self) -> Float:
        from poop.types.float import Float

        return Float(float(self._value))

    def __abs__(self) -> Int:
        return Int(abs(self._value))

    def abs(self) -> Int:
        return self.__abs__()

    def __pos__(self) -> Int:
        return Int(+self._value)

    def pos(self) -> Int:
        return self.__pos__()

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

    def __round__(self, ndigits: int | None = None) -> Int:
        return Int(round(self._value, ndigits))

    def round(self, ndigits: int | None = None) -> Int:
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

    def __hash__(self) -> int:
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

    def __int__(self) -> int:
        return self._value

    def __bool__(self) -> bool:
        return self._value != 0

    def __str__(self) -> str:
        return str(self._value)
