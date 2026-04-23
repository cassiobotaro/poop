from collections import deque
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.string import Str
    from poop.types.tuple import Tuple

_bytearray = bytearray  # alias to avoid shadowing by ByteArray class name


class ByteArray(Object):
    __slots__ = ("_value",)

    def __init__(self, value: _bytearray | None = None) -> None:
        self._value: _bytearray = _bytearray() if value is None else value

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._value))

    def __len__(self) -> int:
        return len(self._value)

    def at(self, index: Int) -> Int:
        from poop.types.int import Int

        return Int(self._value[index._value])

    def copy_from_to(self, start: Int, stop: Int, step: Int | None = None) -> ByteArray:
        s = step._value if step is not None else None
        return ByteArray(bytearray(self._value[start._value : stop._value : s]))

    def __getitem__(self, index: Int) -> Int:
        return self.at(index)

    def at_put(self, index: Int, byte: Int) -> ByteArray:
        self._value[index._value] = byte._value
        return self

    def includes(self, byte: Int) -> Boolean:
        from poop.types.boolean import false, true

        return true if byte._value in self._value else false

    def __contains__(self, item: object) -> bool:
        from poop.types.int import Int

        if isinstance(item, Int):
            return item._value in self._value
        return False

    def decode(self, encoding: Str) -> Str:
        from poop.types.string import Str

        return Str(self._value.decode(encoding._value))

    def hex(self) -> Str:
        from poop.types.string import Str

        return Str(self._value.hex())

    def do(self, block: Callable[[Int], Any]) -> None:
        from poop.types.int import Int

        deque((block(Int(b)) for b in self._value), maxlen=0)

    def map(self, block: Callable[[Int], Any]) -> List:
        from poop.types.int import Int
        from poop.types.list import List

        return List(*(block(Int(b)) for b in self._value))

    def __iter__(self) -> Iterator[Int]:
        from poop.types.int import Int

        return (Int(b) for b in self._value)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, ByteArray):
            return true if self._value == other._value else false
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, ByteArray):
            return false if self._value == other._value else true
        return true

    def append(self, byte: Int) -> ByteArray:
        self._value.append(byte._value)
        return self

    def clear(self) -> ByteArray:
        self._value.clear()
        return self

    def copy(self) -> ByteArray:
        return ByteArray(_bytearray(self._value))

    def extend(self, iterable: ByteArray) -> ByteArray:
        self._value.extend(iterable._value)
        return self

    def insert(self, i: Int, byte: Int) -> ByteArray:
        self._value.insert(i._value, byte._value)
        return self

    def pop(self, index: Int | None = None) -> Int:
        from poop.types.int import Int

        if index is None:
            return Int(self._value.pop())
        return Int(self._value.pop(index._value))

    def remove(self, byte: Int) -> ByteArray:
        self._value.remove(byte._value)
        return self

    def reverse(self) -> ByteArray:
        self._value.reverse()
        return self

    def capitalize(self) -> ByteArray:
        return ByteArray(_bytearray(self._value.capitalize()))

    def center(self, width: Int, fillchar: ByteArray | None = None) -> ByteArray:
        if fillchar is None:
            return ByteArray(_bytearray(self._value.center(width._value)))
        return ByteArray(
            _bytearray(self._value.center(width._value, bytes(fillchar._value)))
        )

    def count(self, sub: ByteArray) -> Int:
        from poop.types.int import Int

        return Int(self._value.count(sub._value))

    def endswith(self, suffix: ByteArray) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.endswith(bytes(suffix._value)) else false

    def expandtabs(self, tabsize: Int | None = None) -> ByteArray:
        if tabsize is None:
            return ByteArray(_bytearray(self._value.expandtabs()))
        return ByteArray(_bytearray(self._value.expandtabs(tabsize._value)))

    def find(self, sub: ByteArray) -> Int:
        from poop.types.int import Int

        return Int(self._value.find(sub._value))

    def index(self, sub: ByteArray) -> Int:
        from poop.types.int import Int

        return Int(self._value.index(sub._value))

    def isalnum(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.isalnum() else false

    def isalpha(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.isalpha() else false

    def isascii(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.isascii() else false

    def isdigit(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.isdigit() else false

    def islower(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.islower() else false

    def isspace(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.isspace() else false

    def istitle(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.istitle() else false

    def isupper(self) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.isupper() else false

    def join(self, parts: List) -> ByteArray:
        pieces: list[_bytearray] = [p._value for p in parts if isinstance(p, ByteArray)]  # type: ignore[unresolved-attribute]
        return ByteArray(_bytearray(self._value.join(pieces)))

    def ljust(self, width: Int, fillchar: ByteArray | None = None) -> ByteArray:
        if fillchar is None:
            return ByteArray(_bytearray(self._value.ljust(width._value)))
        return ByteArray(
            _bytearray(self._value.ljust(width._value, bytes(fillchar._value)))
        )

    def lower(self) -> ByteArray:
        return ByteArray(_bytearray(self._value.lower()))

    def lstrip(self, chars: ByteArray | None = None) -> ByteArray:
        if chars is None:
            return ByteArray(_bytearray(self._value.lstrip()))
        return ByteArray(_bytearray(self._value.lstrip(chars._value)))

    def partition(self, sep: ByteArray) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(
            *[ByteArray(_bytearray(p)) for p in self._value.partition(sep._value)]
        )

    def removeprefix(self, prefix: ByteArray) -> ByteArray:
        return ByteArray(_bytearray(self._value.removeprefix(bytes(prefix._value))))

    def removesuffix(self, suffix: ByteArray) -> ByteArray:
        return ByteArray(_bytearray(self._value.removesuffix(bytes(suffix._value))))

    def replace(self, old: ByteArray, new: ByteArray) -> ByteArray:
        return ByteArray(_bytearray(self._value.replace(old._value, new._value)))

    def rfind(self, sub: ByteArray) -> Int:
        from poop.types.int import Int

        return Int(self._value.rfind(sub._value))

    def rindex(self, sub: ByteArray) -> Int:
        from poop.types.int import Int

        return Int(self._value.rindex(sub._value))

    def rjust(self, width: Int, fillchar: ByteArray | None = None) -> ByteArray:
        if fillchar is None:
            return ByteArray(_bytearray(self._value.rjust(width._value)))
        return ByteArray(
            _bytearray(self._value.rjust(width._value, bytes(fillchar._value)))
        )

    def rpartition(self, sep: ByteArray) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(
            *[ByteArray(_bytearray(p)) for p in self._value.rpartition(sep._value)]
        )

    def rsplit(self, sep: ByteArray | None = None) -> List:
        from poop.types.list import List

        return List(
            *[
                ByteArray(_bytearray(p))
                for p in self._value.rsplit(sep._value if sep is not None else None)
            ]
        )

    def rstrip(self, chars: ByteArray | None = None) -> ByteArray:
        if chars is None:
            return ByteArray(_bytearray(self._value.rstrip()))
        return ByteArray(_bytearray(self._value.rstrip(chars._value)))

    def split(self, sep: ByteArray | None = None) -> List:
        from poop.types.list import List

        if sep is None:
            return List(*[ByteArray(_bytearray(p)) for p in self._value.split()])
        return List(*[ByteArray(_bytearray(p)) for p in self._value.split(sep._value)])

    def splitlines(self) -> List:
        from poop.types.list import List

        return List(*[ByteArray(_bytearray(p)) for p in self._value.splitlines()])

    def startswith(self, prefix: ByteArray) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._value.startswith(bytes(prefix._value)) else false

    def strip(self, chars: ByteArray | None = None) -> ByteArray:
        if chars is None:
            return ByteArray(_bytearray(self._value.strip()))
        return ByteArray(_bytearray(self._value.strip(chars._value)))

    def swapcase(self) -> ByteArray:
        return ByteArray(_bytearray(self._value.swapcase()))

    def title(self) -> ByteArray:
        return ByteArray(_bytearray(self._value.title()))

    def upper(self) -> ByteArray:
        return ByteArray(_bytearray(self._value.upper()))

    def zfill(self, width: Int) -> ByteArray:
        return ByteArray(_bytearray(self._value.zfill(width._value)))

    def __str__(self) -> str:
        return repr(self._value)

    __repr__ = __str__
