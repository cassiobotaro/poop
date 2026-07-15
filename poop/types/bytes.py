from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._iterable_mixin import _IterableMixin
from poop.types._repeat import _repeat_count
from poop.types._unwrap import _is_absent, _unwrap
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import Boolean, false, to_boolean, true
from poop.types.bytes_iterator import BytesIterator
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
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
    _eq_group: ClassVar[str] = "bytes"

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
        stop: Int | NoneClass | None = None,
        step: Int | NoneClass | None = None,
    ) -> Bytes:
        from poop.types.slice import Slice

        if isinstance(start_or_slice, Slice):
            py = start_or_slice._py_slice()
        else:
            py = Slice(start_or_slice, stop, step)._py_slice()
        return Bytes(self._value[py])

    def includes(self, byte: Int) -> Boolean:
        return to_boolean(byte._value in self._value)

    def __contains__(self, item: object) -> bool:
        from poop.types.int import Int

        if isinstance(item, Int):
            return item._value in self._value
        return False

    def decode(
        self,
        encoding: Str | NoneClass | None = None,
        errors: Str | NoneClass | None = None,
    ) -> Str:
        from poop.types._unwrap import _opt_str
        from poop.types.string import Str

        return Str(
            self._value.decode(
                _opt_str(encoding, "utf-8"),
                _opt_str(errors, "strict"),
            )
        )

    def hex(
        self,
        sep: Str | Bytes | NoneClass | None = None,
        bytes_per_sep: Int | NoneClass | None = None,
    ) -> Str:
        from poop.types._unwrap import _opt_int
        from poop.types.string import Str

        if _is_absent(sep):
            return Str(self._value.hex())
        sep_value = sep._value
        return Str(self._value.hex(sep_value, _opt_int(bytes_per_sep, 1)))

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

    def __lt__(self, other: object) -> Boolean:
        if not isinstance(other, Bytes):
            return NotImplemented  # foreign operand -> faithful TypeError
        return to_boolean(self._value < other._value)

    def __le__(self, other: object) -> Boolean:
        if not isinstance(other, Bytes):
            return NotImplemented
        return to_boolean(self._value <= other._value)

    def __gt__(self, other: object) -> Boolean:
        if not isinstance(other, Bytes):
            return NotImplemented
        return to_boolean(self._value > other._value)

    def __ge__(self, other: object) -> Boolean:
        if not isinstance(other, Bytes):
            return NotImplemented
        return to_boolean(self._value >= other._value)

    def __add__(self, other: Bytes) -> Bytes:
        return Bytes(self._value + other._value)

    def __mul__(self, other: object) -> Bytes:
        return Bytes(self._value * _repeat_count(other))

    def __rmul__(self, other: object) -> Bytes:
        return Bytes(self._value * _repeat_count(other))

    def capitalize(self) -> Bytes:
        return Bytes(self._value.capitalize())

    def center(self, width: Int, fillchar: Bytes | NoneClass | None = None) -> Bytes:
        fill = _unwrap(fillchar, None)
        if fill is None:
            return Bytes(self._value.center(width._value))
        return Bytes(self._value.center(width._value, fill))

    def count(
        self,
        sub: Bytes,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.count(sub._value, _unwrap(start, None), _unwrap(end, None))
        )

    def endswith(
        self,
        suffix: Bytes,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return (
            true
            if self._value.endswith(
                suffix._value, _unwrap(start, None), _unwrap(end, None)
            )
            else false
        )

    def expandtabs(self, tabsize: Int | NoneClass | None = None) -> Bytes:
        size = _unwrap(tabsize, None)
        if size is None:
            return Bytes(self._value.expandtabs())
        return Bytes(self._value.expandtabs(size))

    def find(
        self,
        sub: Bytes,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.find(sub._value, _unwrap(start, None), _unwrap(end, None))
        )

    def index(
        self,
        sub: Bytes,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.index(sub._value, _unwrap(start, None), _unwrap(end, None))
        )

    def isalnum(self) -> Boolean:
        return to_boolean(self._value.isalnum())

    def isalpha(self) -> Boolean:
        return to_boolean(self._value.isalpha())

    def isascii(self) -> Boolean:
        return to_boolean(self._value.isascii())

    def isdigit(self) -> Boolean:
        return to_boolean(self._value.isdigit())

    def islower(self) -> Boolean:
        return to_boolean(self._value.islower())

    def isspace(self) -> Boolean:
        return to_boolean(self._value.isspace())

    def istitle(self) -> Boolean:
        return to_boolean(self._value.istitle())

    def isupper(self) -> Boolean:
        return to_boolean(self._value.isupper())

    def join(self, parts: List) -> Bytes:
        # Mirror CPython: unwrap each element to its underlying value and let
        # bytes.join validate. Bytes-like POOP wrappers (Bytes/ByteArray/
        # MemoryView) join cleanly; anything else (Str, Int, ...) reaches
        # bytes.join unwrapped and raises the faithful TypeError instead of
        # being silently dropped.
        pieces: list[Any] = [getattr(p, "_value", p) for p in parts]
        return Bytes(self._value.join(pieces))

    def ljust(self, width: Int, fillchar: Bytes | NoneClass | None = None) -> Bytes:
        fill = _unwrap(fillchar, None)
        if fill is None:
            return Bytes(self._value.ljust(width._value))
        return Bytes(self._value.ljust(width._value, fill))

    def lower(self) -> Bytes:
        return Bytes(self._value.lower())

    def lstrip(self, chars: Bytes | NoneClass | None = None) -> Bytes:
        return Bytes(self._value.lstrip(_unwrap(chars, None)))

    def partition(self, sep: Bytes) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*[Bytes(p) for p in self._value.partition(sep._value)])

    def removeprefix(self, prefix: Bytes) -> Bytes:
        return Bytes(self._value.removeprefix(prefix._value))

    def removesuffix(self, suffix: Bytes) -> Bytes:
        return Bytes(self._value.removesuffix(suffix._value))

    def replace(
        self,
        old: Bytes,
        new: Bytes,
        count: Int | NoneClass | None = None,
    ) -> Bytes:
        return Bytes(self._value.replace(old._value, new._value, _unwrap(count, -1)))

    def rfind(
        self,
        sub: Bytes,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.rfind(sub._value, _unwrap(start, None), _unwrap(end, None))
        )

    def rindex(
        self,
        sub: Bytes,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.rindex(sub._value, _unwrap(start, None), _unwrap(end, None))
        )

    def rjust(self, width: Int, fillchar: Bytes | NoneClass | None = None) -> Bytes:
        fill = _unwrap(fillchar, None)
        if fill is None:
            return Bytes(self._value.rjust(width._value))
        return Bytes(self._value.rjust(width._value, fill))

    def rpartition(self, sep: Bytes) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*[Bytes(p) for p in self._value.rpartition(sep._value)])

    def rsplit(
        self,
        sep: Bytes | NoneClass | None = None,
        maxsplit: Int | NoneClass | None = None,
    ) -> List:
        from poop.types.list import List

        return List(
            *[
                Bytes(p)
                for p in self._value.rsplit(_unwrap(sep, None), _unwrap(maxsplit, -1))
            ]
        )

    def rstrip(self, chars: Bytes | NoneClass | None = None) -> Bytes:
        return Bytes(self._value.rstrip(_unwrap(chars, None)))

    def split(
        self,
        sep: Bytes | NoneClass | None = None,
        maxsplit: Int | NoneClass | None = None,
    ) -> List:
        from poop.types.list import List

        return List(
            *[
                Bytes(p)
                for p in self._value.split(_unwrap(sep, None), _unwrap(maxsplit, -1))
            ]
        )

    def splitlines(self, keepends: Boolean | NoneClass | None = None) -> List:
        from poop.types._unwrap import _unwrap_bool
        from poop.types.list import List

        return List(
            *[Bytes(p) for p in self._value.splitlines(_unwrap_bool(keepends, False))]
        )

    def startswith(
        self,
        prefix: Bytes,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return (
            true
            if self._value.startswith(
                prefix._value, _unwrap(start, None), _unwrap(end, None)
            )
            else false
        )

    def strip(self, chars: Bytes | NoneClass | None = None) -> Bytes:
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


Bytes.__module__ = "builtins"
Bytes.__name__ = "bytes"
