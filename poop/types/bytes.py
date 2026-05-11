from collections.abc import Iterator
from typing import TYPE_CHECKING, ClassVar

from poop.types._iterable_mixin import _IterableMixin
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import false, true
from poop.types.bytes_iterator import BytesIterator
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.none import NoneClass
    from poop.types.slice import Slice
    from poop.types.string import Str
    from poop.types.tuple import Tuple

_bytes = bytes  # alias to avoid shadowing by Bytes class name in annotations


class Bytes(_ValueEqMixin, _IterableMixin, Object):
    __slots__ = ("_value",)
    _eq_attr: ClassVar[str] = "_value"

    def __init__(self, value: _bytes | Bytes) -> None:
        self._value = value._value if isinstance(value, Bytes) else value

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._value))

    def __len__(self) -> int:
        return len(self._value)

    def at(self, index: Int) -> Int:
        from poop.types.int import Int

        return Int(self._value[index._value])

    def slice(
        self,
        start_or_slice: Int | Slice,
        stop: Int | None = None,
        step: Int | None = None,
    ) -> Bytes:
        from poop.types.slice import Slice

        if isinstance(start_or_slice, Slice):
            s = (
                start_or_slice._step._value
                if start_or_slice._step is not None
                else None
            )
            return Bytes(
                self._value[
                    start_or_slice._start._value : start_or_slice._stop._value : s
                ]
            )
        if stop is None:
            raise TypeError("stop is required when start is an Int")
        s = step._value if step is not None else None
        return Bytes(self._value[start_or_slice._value : stop._value : s])

    def includes(self, byte: Int) -> Boolean:
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

    @classmethod
    def fromhex(cls, s: Str) -> Bytes:
        return cls(bytes.fromhex(s._value))

    def __iter__(self) -> Iterator[Int]:
        from poop.types.int import Int

        return (Int(b) for b in self._value)

    def iter(self) -> BytesIterator:
        return BytesIterator(self)

    def __hash__(self) -> int:
        return hash(self._value)

    def __add__(self, other: Bytes) -> Bytes:
        return Bytes(self._value + other._value)

    def __mul__(self, other: Int) -> Bytes:
        return Bytes(self._value * other._value)

    def capitalize(self) -> Bytes:
        return Bytes(self._value.capitalize())

    def center(self, width: Int, fillchar: Bytes | NoneClass | None = None) -> Bytes:
        from poop.types._unwrap import _unwrap

        fill = _unwrap(fillchar, None)
        if fill is None:
            return Bytes(self._value.center(width._value))
        return Bytes(self._value.center(width._value, fill))

    def count(self, sub: Bytes) -> Int:
        from poop.types.int import Int

        return Int(self._value.count(sub._value))

    def endswith(self, suffix: Bytes) -> Boolean:
        return true if self._value.endswith(suffix._value) else false

    def expandtabs(self, tabsize: Int | NoneClass | None = None) -> Bytes:
        from poop.types._unwrap import _unwrap

        size = _unwrap(tabsize, None)
        if size is None:
            return Bytes(self._value.expandtabs())
        return Bytes(self._value.expandtabs(size))

    def find(self, sub: Bytes) -> Int:
        from poop.types.int import Int

        return Int(self._value.find(sub._value))

    def index(self, sub: Bytes) -> Int:
        from poop.types.int import Int

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

    def join(self, parts: List) -> Bytes:
        pieces: list[_bytes] = [p._value for p in parts if isinstance(p, Bytes)]  # type: ignore[unresolved-attribute]
        return Bytes(self._value.join(pieces))

    def ljust(self, width: Int, fillchar: Bytes | NoneClass | None = None) -> Bytes:
        from poop.types._unwrap import _unwrap

        fill = _unwrap(fillchar, None)
        if fill is None:
            return Bytes(self._value.ljust(width._value))
        return Bytes(self._value.ljust(width._value, fill))

    def lower(self) -> Bytes:
        return Bytes(self._value.lower())

    def lstrip(self, chars: Bytes | NoneClass | None = None) -> Bytes:
        from poop.types._unwrap import _unwrap

        return Bytes(self._value.lstrip(_unwrap(chars, None)))

    def partition(self, sep: Bytes) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*[Bytes(p) for p in self._value.partition(sep._value)])

    def removeprefix(self, prefix: Bytes) -> Bytes:
        return Bytes(self._value.removeprefix(prefix._value))

    def removesuffix(self, suffix: Bytes) -> Bytes:
        return Bytes(self._value.removesuffix(suffix._value))

    def replace(self, old: Bytes, new: Bytes) -> Bytes:
        return Bytes(self._value.replace(old._value, new._value))

    def rfind(self, sub: Bytes) -> Int:
        from poop.types.int import Int

        return Int(self._value.rfind(sub._value))

    def rindex(self, sub: Bytes) -> Int:
        from poop.types.int import Int

        return Int(self._value.rindex(sub._value))

    def rjust(self, width: Int, fillchar: Bytes | NoneClass | None = None) -> Bytes:
        from poop.types._unwrap import _unwrap

        fill = _unwrap(fillchar, None)
        if fill is None:
            return Bytes(self._value.rjust(width._value))
        return Bytes(self._value.rjust(width._value, fill))

    def rpartition(self, sep: Bytes) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*[Bytes(p) for p in self._value.rpartition(sep._value)])

    def rsplit(self, sep: Bytes | NoneClass | None = None) -> List:
        from poop.types._unwrap import _unwrap
        from poop.types.list import List

        return List(*[Bytes(p) for p in self._value.rsplit(_unwrap(sep, None))])

    def rstrip(self, chars: Bytes | NoneClass | None = None) -> Bytes:
        from poop.types._unwrap import _unwrap

        return Bytes(self._value.rstrip(_unwrap(chars, None)))

    def split(self, sep: Bytes | NoneClass | None = None) -> List:
        from poop.types._unwrap import _unwrap
        from poop.types.list import List

        return List(*[Bytes(p) for p in self._value.split(_unwrap(sep, None))])

    def splitlines(self) -> List:
        from poop.types.list import List

        return List(*[Bytes(p) for p in self._value.splitlines()])

    def startswith(self, prefix: Bytes) -> Boolean:
        return true if self._value.startswith(prefix._value) else false

    def strip(self, chars: Bytes | NoneClass | None = None) -> Bytes:
        from poop.types._unwrap import _unwrap

        return Bytes(self._value.strip(_unwrap(chars, None)))

    def swapcase(self) -> Bytes:
        return Bytes(self._value.swapcase())

    def title(self) -> Bytes:
        return Bytes(self._value.title())

    def upper(self) -> Bytes:
        return Bytes(self._value.upper())

    def zfill(self, width: Int) -> Bytes:
        return Bytes(self._value.zfill(width._value))

    def __str__(self) -> str:
        return repr(self._value)

    __repr__ = __str__
