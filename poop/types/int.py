from __future__ import annotations

from collections.abc import Callable

from poop.types.object import Object


class Int(Object):
    def __init__(self, value: int) -> None:
        self._value = value

    def negated(self) -> Int:
        return Int(-self._value)

    def bit_invert(self) -> Int:
        return Int(~self._value)

    def times_repeat[T](self, block: Callable[[], T]) -> None:
        for _ in range(self._value):
            block()

    def to_do[T](self, limit: Int, block: Callable[[Int], T]) -> None:
        for i in range(self._value, limit._value + 1):
            block(Int(i))

    def max(self, other: Int) -> Int:
        return self if self._value >= other._value else other

    def min(self, other: Int) -> Int:
        return self if self._value <= other._value else other

    def __add__(self, other: Int) -> Int:
        return Int(self._value + other._value)

    def __sub__(self, other: Int) -> Int:
        return Int(self._value - other._value)

    def __mul__(self, other: Int) -> Int:
        return Int(self._value * other._value)

    def __floordiv__(self, other: Int) -> Int:
        return Int(self._value // other._value)

    def __mod__(self, other: Int) -> Int:
        return Int(self._value % other._value)

    def __pow__(self, other: Int) -> Int:
        return Int(self._value**other._value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Int):
            return self._value == other._value
        return NotImplemented

    def __lt__(self, other: Int) -> bool:
        return self._value < other._value

    def __le__(self, other: Int) -> bool:
        return self._value <= other._value

    def __gt__(self, other: Int) -> bool:
        return self._value > other._value

    def __ge__(self, other: Int) -> bool:
        return self._value >= other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __int__(self) -> int:
        return self._value

    def __bool__(self) -> bool:
        return self._value != 0

    def __str__(self) -> str:
        return str(self._value)
