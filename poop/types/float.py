from __future__ import annotations

from poop.types.object import Object


class Float(Object):
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

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Float):
            return self._value == other._value
        return NotImplemented

    def __lt__(self, other: Float) -> bool:
        return self._value < other._value

    def __le__(self, other: Float) -> bool:
        return self._value <= other._value

    def __gt__(self, other: Float) -> bool:
        return self._value > other._value

    def __ge__(self, other: Float) -> bool:
        return self._value >= other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __float__(self) -> float:
        return self._value

    def __bool__(self) -> bool:
        return self._value != 0.0

    def __str__(self) -> str:
        return str(self._value)
