from collections.abc import Iterator
from typing import TYPE_CHECKING

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.float import Float
    from poop.types.int import Int

_int = int  # alias to avoid shadowing by Str.int() method
_str = str  # alias to avoid shadowing in annotations


class Str(Object):
    __slots__ = ("_value",)

    def __init__(self, value: _str) -> None:
        self._value = value

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._value))

    def __len__(self) -> _int:
        return len(self._value)

    def ord(self) -> Int:
        from poop.types.int import Int

        return Int(ord(self._value))

    def int(self) -> Int:
        from poop.types.int import Int

        return Int(_int(self._value))

    def float(self) -> Float:
        from poop.types.float import Float

        return Float(float(self._value))

    def at(self, index: Int) -> Str:
        return Str(self._value[index._value])

    def __getitem__(self, index: Int) -> Str:
        return self.at(index)

    def __iter__(self) -> Iterator[Str]:
        for ch in self._value:
            yield Str(ch)

    def includes(self, char: Str) -> Boolean:
        from poop.types.boolean import false, true

        return true if char._value in self._value else false

    def __contains__(self, item: object) -> bool:
        if isinstance(item, Str):
            return item._value in self._value
        return False

    def reversed(self) -> Str:
        return Str(self._value[::-1])

    def upper(self) -> Str:
        return Str(self._value.upper())

    def lower(self) -> Str:
        return Str(self._value.lower())

    def capitalize(self) -> Str:
        return Str(self._value.capitalize())

    def title(self) -> Str:
        return Str(self._value.title())

    def swapcase(self) -> Str:
        return Str(self._value.swapcase())

    def strip(self) -> Str:
        return Str(self._value.strip())

    def lstrip(self) -> Str:
        return Str(self._value.lstrip())

    def rstrip(self) -> Str:
        return Str(self._value.rstrip())

    def replace(self, old: Str, new: Str) -> Str:
        return Str(self._value.replace(old._value, new._value))

    def split(self, sep: Str | None = None) -> list[Str]:
        if sep is None:
            return [Str(p) for p in self._value.split()]
        return [Str(p) for p in self._value.split(sep._value)]

    def join(self, parts: list[Str]) -> Str:
        return Str(self._value.join(p._value for p in parts))

    def find(self, sub: Str) -> Int:
        from poop.types.int import Int

        return Int(self._value.find(sub._value))

    def index(self, sub: Str) -> Int:
        from poop.types.int import Int

        return Int(self._value.index(sub._value))

    def count(self, sub: Str) -> Int:
        from poop.types.int import Int

        return Int(self._value.count(sub._value))

    def startswith(self, prefix: Str) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.startswith(prefix._value) else false

    def endswith(self, suffix: Str) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.endswith(suffix._value) else false

    def isalpha(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.isalpha() else false

    def isdigit(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.isdigit() else false

    def isalnum(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.isalnum() else false

    def isspace(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.isspace() else false

    def isupper(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.isupper() else false

    def islower(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.islower() else false

    def __add__(self, other: Str) -> Str:
        return Str(self._value + other._value)

    def __mul__(self, other: Int) -> Str:
        return Str(self._value * other._value)

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

    def __lt__(self, other: Str) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value < other._value else false

    def __le__(self, other: Str) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value <= other._value else false

    def __gt__(self, other: Str) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value > other._value else false

    def __ge__(self, other: Str) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value >= other._value else false

    def __hash__(self) -> _int:
        return hash(self._value)

    def __str__(self) -> _str:
        return self._value
