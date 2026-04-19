from typing import TYPE_CHECKING

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class Float(Object):
    __slots__ = ("_value",)

    def __init__(self, value: float) -> None:
        self._value = value

    def negated(self) -> Float:
        return Float(-self._value)

    def max(self, other: Float) -> Float:
        return self if self._value >= other._value else other

    def min(self, other: Float) -> Float:
        return self if self._value <= other._value else other

    def __add__(self, other: Float) -> Float:
        return Float(self._value + other._value)

    def __sub__(self, other: Float) -> Float:
        return Float(self._value - other._value)

    def __mul__(self, other: Float) -> Float:
        return Float(self._value * other._value)

    def __truediv__(self, other: Float) -> Float:
        return Float(self._value / other._value)

    def __mod__(self, other: Float) -> Float:
        return Float(self._value % other._value)

    def __pow__(self, other: Float) -> Float:
        return Float(self._value**other._value)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Float):
            return true if self._value == other._value else false
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Float):
            return false if self._value == other._value else true
        return true

    def __lt__(self, other: Float) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value < other._value else false

    def __le__(self, other: Float) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value <= other._value else false

    def __gt__(self, other: Float) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value > other._value else false

    def __ge__(self, other: Float) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value >= other._value else false

    def __hash__(self) -> int:
        return hash(self._value)

    def __float__(self) -> float:
        return self._value

    def __bool__(self) -> bool:
        return self._value != 0.0

    def __str__(self) -> str:
        return str(self._value)
