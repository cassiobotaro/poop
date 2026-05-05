from collections.abc import Iterator
from typing import TYPE_CHECKING

from poop.types.boolean import Boolean, false, true
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.bytes import Bytes
    from poop.types.float import Float
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.tuple import Tuple

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

    def slice(self, start: Int, stop: Int, step: Int | None = None) -> Str:
        s = step._value if step is not None else None
        return Str(self._value[start._value : stop._value : s])

    def __iter__(self) -> Iterator[Str]:
        for ch in self._value:
            yield Str(ch)

    def includes(self, char: Str) -> Boolean:
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

    def split(self, sep: Str | None = None) -> List:
        from poop.types.list import List

        if sep is None:
            return List(*(Str(p) for p in self._value.split()))
        return List(*(Str(p) for p in self._value.split(sep._value)))

    def join(self, parts: List) -> Str:
        return Str(self._value.join(str(p) for p in parts))

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
        return true if self._value.startswith(prefix._value) else false

    def endswith(self, suffix: Str) -> Boolean:
        return true if self._value.endswith(suffix._value) else false

    def isalpha(self) -> Boolean:
        return true if self._value.isalpha() else false

    def isdigit(self) -> Boolean:
        return true if self._value.isdigit() else false

    def isalnum(self) -> Boolean:
        return true if self._value.isalnum() else false

    def isspace(self) -> Boolean:
        return true if self._value.isspace() else false

    def isupper(self) -> Boolean:
        return true if self._value.isupper() else false

    def islower(self) -> Boolean:
        return true if self._value.islower() else false

    def casefold(self) -> Str:
        return Str(self._value.casefold())

    def center(self, width: Int, fillchar: Str | None = None) -> Str:
        if fillchar is None:
            return Str(self._value.center(width._value))
        return Str(self._value.center(width._value, fillchar._value))

    def encode(self, encoding: Str) -> Bytes:
        from poop.types.bytes import Bytes

        return Bytes(self._value.encode(encoding._value))

    def expandtabs(self, tabsize: Int | None = None) -> Str:
        if tabsize is None:
            return Str(self._value.expandtabs())
        return Str(self._value.expandtabs(tabsize._value))

    def isascii(self) -> Boolean:
        return true if self._value.isascii() else false

    def isdecimal(self) -> Boolean:
        return true if self._value.isdecimal() else false

    def isidentifier(self) -> Boolean:
        return true if self._value.isidentifier() else false

    def isnumeric(self) -> Boolean:
        return true if self._value.isnumeric() else false

    def isprintable(self) -> Boolean:
        return true if self._value.isprintable() else false

    def istitle(self) -> Boolean:
        return true if self._value.istitle() else false

    def ljust(self, width: Int, fillchar: Str | None = None) -> Str:
        if fillchar is None:
            return Str(self._value.ljust(width._value))
        return Str(self._value.ljust(width._value, fillchar._value))

    def rjust(self, width: Int, fillchar: Str | None = None) -> Str:
        if fillchar is None:
            return Str(self._value.rjust(width._value))
        return Str(self._value.rjust(width._value, fillchar._value))

    def zfill(self, width: Int) -> Str:
        return Str(self._value.zfill(width._value))

    def partition(self, sep: Str) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*[Str(s) for s in self._value.partition(sep._value)])

    def rpartition(self, sep: Str) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*[Str(s) for s in self._value.rpartition(sep._value)])

    def removeprefix(self, prefix: Str) -> Str:
        return Str(self._value.removeprefix(prefix._value))

    def removesuffix(self, suffix: Str) -> Str:
        return Str(self._value.removesuffix(suffix._value))

    def rfind(self, sub: Str) -> Int:
        from poop.types.int import Int

        return Int(self._value.rfind(sub._value))

    def rindex(self, sub: Str) -> Int:
        from poop.types.int import Int

        return Int(self._value.rindex(sub._value))

    def rsplit(self, sep: Str | None = None) -> List:
        from poop.types.list import List

        return List(
            *[
                Str(s)
                for s in self._value.rsplit(sep._value if sep is not None else None)
            ]
        )

    def splitlines(self) -> List:
        from poop.types.list import List

        return List(*[Str(s) for s in self._value.splitlines()])

    def __add__(self, other: Str) -> Str:
        return Str(self._value + other._value)

    def __mul__(self, other: Int) -> Str:
        return Str(self._value * other._value)

    def __rmul__(self, other: Int) -> Str:
        return Str(self._value * other._value)

    def __eq__(self, other: object) -> Boolean:
        if isinstance(other, Str):
            return true if self._value == other._value else false
        return false

    def __ne__(self, other: object) -> Boolean:
        if isinstance(other, Str):
            return false if self._value == other._value else true
        return true

    def __lt__(self, other: Str) -> Boolean:
        return true if self._value < other._value else false

    def __le__(self, other: Str) -> Boolean:
        return true if self._value <= other._value else false

    def __gt__(self, other: Str) -> Boolean:
        return true if self._value > other._value else false

    def __ge__(self, other: Str) -> Boolean:
        return true if self._value >= other._value else false

    def __hash__(self) -> _int:
        return hash(self._value)

    def __str__(self) -> _str:
        return self._value

    def __repr__(self) -> _str:
        return repr(self._value)
