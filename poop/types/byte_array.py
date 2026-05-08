from collections.abc import Iterator
from typing import TYPE_CHECKING

from poop.types._iterable_mixin import _IterableMixin
from poop.types.boolean import false, true
from poop.types.byte_array_iterator import ByteArrayIterator
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.none import NoneClass
    from poop.types.slice import Slice

_bytearray = bytearray  # alias to avoid shadowing by ByteArray class name


class ByteArray(_IterableMixin, Object):
    __slots__ = ("_value",)
    __hash__ = None

    def __init__(self, value: _bytearray | ByteArray | None = None) -> None:
        if value is None:
            self._value: _bytearray = _bytearray()
        elif isinstance(value, ByteArray):
            self._value = value._value
        else:
            self._value = value

    def len(self) -> Int:
        return Int(len(self._value))

    def __len__(self) -> int:
        return len(self._value)

    def at(self, index: Int) -> Int:
        return Int(self._value[index._value])

    def slice(
        self,
        start_or_slice: Int | Slice,
        stop: Int | None = None,
        step: Int | None = None,
    ) -> ByteArray:
        from poop.types.slice import Slice

        if isinstance(start_or_slice, Slice):
            s = (
                start_or_slice._step._value
                if start_or_slice._step is not None
                else None
            )
            return ByteArray(
                bytearray(
                    self._value[
                        start_or_slice._start._value : start_or_slice._stop._value : s
                    ]
                )
            )
        if stop is None:
            raise TypeError("stop is required when start is an Int")
        s = step._value if step is not None else None
        return ByteArray(
            bytearray(self._value[start_or_slice._value : stop._value : s])
        )

    def at_put(self, index: Int, byte: Int) -> ByteArray:
        self._value[index._value] = byte._value
        return self

    def includes(self, byte: Int) -> Boolean:
        return true if byte._value in self._value else false

    def __contains__(self, item: object) -> bool:
        if isinstance(item, Int):
            return item._value in self._value
        return False

    def decode(self, encoding: Str) -> Str:
        return Str(self._value.decode(encoding._value))

    def hex(self) -> Str:
        return Str(self._value.hex())

    def __iter__(self) -> Iterator[Int]:
        return (Int(b) for b in self._value)

    def iter(self) -> ByteArrayIterator:
        return ByteArrayIterator(self)

    def __eq__(self, other: object) -> Boolean:
        if isinstance(other, ByteArray):
            return true if self._value == other._value else false
        return false

    def __ne__(self, other: object) -> Boolean:
        if isinstance(other, ByteArray):
            return false if self._value == other._value else true
        return true

    def __add__(self, other: ByteArray) -> ByteArray:
        return ByteArray(_bytearray(self._value + other._value))

    def __mul__(self, other: Int) -> ByteArray:
        return ByteArray(_bytearray(self._value * other._value))

    def append(self, byte: Int) -> NoneClass:
        self._value.append(byte._value)
        return none

    def clear(self) -> NoneClass:
        self._value.clear()
        return none

    def copy(self) -> ByteArray:
        return ByteArray(_bytearray(self._value))

    def extend(self, iterable: ByteArray) -> NoneClass:
        self._value.extend(iterable._value)
        return none

    def insert(self, i: Int, byte: Int) -> NoneClass:
        self._value.insert(i._value, byte._value)
        return none

    def pop(self, index: Int | None = None) -> Int:
        if index is None:
            return Int(self._value.pop())
        return Int(self._value.pop(index._value))

    def remove(self, byte: Int) -> NoneClass:
        self._value.remove(byte._value)
        return none

    def reverse(self) -> NoneClass:
        self._value.reverse()
        return none

    def capitalize(self) -> ByteArray:
        return ByteArray(_bytearray(self._value.capitalize()))

    def center(self, width: Int, fillchar: ByteArray | None = None) -> ByteArray:
        if fillchar is None:
            return ByteArray(_bytearray(self._value.center(width._value)))
        return ByteArray(
            _bytearray(self._value.center(width._value, bytes(fillchar._value)))
        )

    def count(self, sub: ByteArray) -> Int:
        return Int(self._value.count(sub._value))

    def endswith(self, suffix: ByteArray) -> Boolean:
        return true if self._value.endswith(bytes(suffix._value)) else false

    def expandtabs(self, tabsize: Int | None = None) -> ByteArray:
        if tabsize is None:
            return ByteArray(_bytearray(self._value.expandtabs()))
        return ByteArray(_bytearray(self._value.expandtabs(tabsize._value)))

    def find(self, sub: ByteArray) -> Int:
        return Int(self._value.find(sub._value))

    def index(self, sub: ByteArray) -> Int:
        return Int(self._value.index(sub._value))

    def isalnum(self) -> Boolean:
        return true if self._value.isalnum() else false

    def isalpha(self) -> Boolean:
        return true if self._value.isalpha() else false

    def isascii(self) -> Boolean:
        return true if self._value.isascii() else false

    def isdigit(self) -> Boolean:
        return true if self._value.isdigit() else false

    def islower(self) -> Boolean:
        return true if self._value.islower() else false

    def isspace(self) -> Boolean:
        return true if self._value.isspace() else false

    def istitle(self) -> Boolean:
        return true if self._value.istitle() else false

    def isupper(self) -> Boolean:
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
        return Int(self._value.rfind(sub._value))

    def rindex(self, sub: ByteArray) -> Int:
        return Int(self._value.rindex(sub._value))

    def rjust(self, width: Int, fillchar: ByteArray | None = None) -> ByteArray:
        if fillchar is None:
            return ByteArray(_bytearray(self._value.rjust(width._value)))
        return ByteArray(
            _bytearray(self._value.rjust(width._value, bytes(fillchar._value)))
        )

    def rpartition(self, sep: ByteArray) -> Tuple:
        return Tuple(
            *[ByteArray(_bytearray(p)) for p in self._value.rpartition(sep._value)]
        )

    def rsplit(self, sep: ByteArray | None = None) -> List:
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
        if sep is None:
            return List(*[ByteArray(_bytearray(p)) for p in self._value.split()])
        return List(*[ByteArray(_bytearray(p)) for p in self._value.split(sep._value)])

    def splitlines(self) -> List:
        return List(*[ByteArray(_bytearray(p)) for p in self._value.splitlines()])

    def startswith(self, prefix: ByteArray) -> Boolean:
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
