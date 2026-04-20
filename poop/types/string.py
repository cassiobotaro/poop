from typing import TYPE_CHECKING

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int


class Str(Object):
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        self._value = value

    def size(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._value))

    def at(self, index: Int) -> Str:
        return Str(self._value[index._value])

    def includes(self, char: Str) -> Boolean:
        from poop.types.boolean import false, true

        return true if char._value in self._value else false

    def reversed(self) -> Str:
        return Str(self._value[::-1])

    def __add__(self, other: Str) -> Str:
        return Str(self._value + other._value)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Str):
            return true if self._value == other._value else false
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Str):
            return false if self._value == other._value else true
        return true

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return self._value
