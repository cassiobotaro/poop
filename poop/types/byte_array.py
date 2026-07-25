from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._iterable_mixin import _IterableMixin
from poop.types._repeat import _repeat_count
from poop.types._unwrap import _faithful, _unwrap
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import false, to_boolean, true
from poop.types.byte_array_iterator import ByteArrayIterator
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.none import NoneClass
    from poop.types.slice import Slice

_bytearray = bytearray  # alias to avoid shadowing by ByteArray class name


class ByteArray(_ValueEqMixin, _IterableMixin, Object):
    __slots__ = ("_value",)
    _eq_attr: ClassVar[str] = "_value"
    _eq_group: ClassVar[str] = "bytes"
    __hash__ = None

    def __init__(
        self,
        value: _bytearray | bytes | ByteArray | Iterable[int] | None = None,
    ) -> None:
        if value is None:
            self._value: _bytearray = _bytearray()
        elif isinstance(value, ByteArray):
            self._value = _bytearray(value._value)
        else:
            self._value = _bytearray(value)

    def len(self) -> Int:
        return Int(len(self._value))

    def __len__(self) -> int:
        return len(self._value)

    def at(self, index: Int) -> Int:
        return Int(self._value[_faithful(index)])

    def slice(
        self,
        start_or_slice: Int | Slice,
        stop: Int | NoneClass | None = None,
        step: Int | NoneClass | None = None,
    ) -> ByteArray:
        from poop.types.slice import _resolve_py_slice

        py = _resolve_py_slice(start_or_slice, stop, step)
        return ByteArray(bytearray(self._value[py]))

    def at_put(self, index: Int, byte: Int) -> ByteArray:
        self._value[_faithful(index)] = _faithful(byte)
        return self

    def includes(self, byte: Int) -> Boolean:
        # getattr-unwrap: a non-`_value` argument reaches bytearray.__contains__
        # raw and raises the faithful TypeError instead of leaking `_value`.
        operand: Any = _faithful(byte)
        return to_boolean(operand in self._value)

    def __contains__(self, item: object) -> bool:
        if isinstance(item, Int):
            return item._value in self._value
        return False

    def decode(
        self,
        encoding: Str | NoneClass | None = None,
        errors: Str | NoneClass | None = None,
    ) -> Str:
        from poop.types._unwrap import _opt_str

        return Str(
            self._value.decode(
                _opt_str(encoding, "utf-8"),
                _opt_str(errors, "strict"),
            )
        )

    def hex(
        self,
        sep: Str | ByteArray | NoneClass | None = None,
        bytes_per_sep: Int | NoneClass | None = None,
    ) -> Str:
        from poop.types._unwrap import _is_absent, _opt_int

        if _is_absent(sep):
            return Str(self._value.hex())
        raw = _faithful(sep)
        sep_value: str | bytes = raw if isinstance(raw, str) else bytes(raw)
        return Str(self._value.hex(sep_value, _opt_int(bytes_per_sep, 1)))

    def __iter__(self) -> Iterator[Int]:
        return (Int(b) for b in self._value)

    def iter(self) -> ByteArrayIterator:
        return ByteArrayIterator(self)

    def __lt__(self, other: object) -> Boolean:
        if not isinstance(other, ByteArray):
            return NotImplemented  # foreign operand -> faithful TypeError
        return to_boolean(self._value < other._value)

    def __le__(self, other: object) -> Boolean:
        if not isinstance(other, ByteArray):
            return NotImplemented
        return to_boolean(self._value <= other._value)

    def __gt__(self, other: object) -> Boolean:
        if not isinstance(other, ByteArray):
            return NotImplemented
        return to_boolean(self._value > other._value)

    def __ge__(self, other: object) -> Boolean:
        if not isinstance(other, ByteArray):
            return NotImplemented
        return to_boolean(self._value >= other._value)

    def __add__(self, other: object) -> ByteArray:
        # Both byte-likes pass: CPython concatenates `bytearray + bytes` and
        # answers bytearray. Anything else -> faithful TypeError, not #_value.
        from poop.types.bytes import Bytes  # circular: bytes imports ByteArray

        if not isinstance(other, ByteArray | Bytes):
            return NotImplemented
        return ByteArray(self._value + other._value)

    def __mul__(self, other: object) -> ByteArray:
        return ByteArray(self._value * _repeat_count(other))

    def __rmul__(self, other: object) -> ByteArray:
        return ByteArray(self._value * _repeat_count(other))

    def append(self, byte: Int) -> NoneClass:
        self._value.append(_faithful(byte))
        return none

    def clear(self) -> NoneClass:
        self._value.clear()
        return none

    def copy(self) -> ByteArray:
        return ByteArray(self._value)

    def extend(self, iterable: ByteArray) -> NoneClass:
        self._value.extend(_faithful(iterable))
        return none

    def insert(self, i: Int, byte: Int) -> NoneClass:
        self._value.insert(_faithful(i), _faithful(byte))
        return none

    def pop(self, index: Int | NoneClass | None = None) -> Int:
        from poop.types._unwrap import _is_absent

        if _is_absent(index):
            return Int(self._value.pop())
        return Int(self._value.pop(_faithful(index)))

    def remove(self, byte: Int) -> NoneClass:
        self._value.remove(_faithful(byte))
        return none

    def reverse(self) -> NoneClass:
        self._value.reverse()
        return none

    def capitalize(self) -> ByteArray:
        return ByteArray(self._value.capitalize())

    def center(
        self,
        width: Int,
        fillchar: ByteArray | NoneClass | None = None,
    ) -> ByteArray:

        fill = _unwrap(fillchar, None)
        if fill is None:
            return ByteArray(self._value.center(_faithful(width)))
        return ByteArray(self._value.center(_faithful(width), bytes(fill)))

    def count(
        self,
        sub: ByteArray,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return Int(
            self._value.count(_faithful(sub), _unwrap(start, None), _unwrap(end, None))
        )

    def endswith(
        self,
        suffix: ByteArray,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return (
            true
            if self._value.endswith(
                bytes(_faithful(suffix)),
                _unwrap(start, None),
                _unwrap(end, None),
            )
            else false
        )

    def expandtabs(self, tabsize: Int | NoneClass | None = None) -> ByteArray:

        size = _unwrap(tabsize, None)
        if size is None:
            return ByteArray(self._value.expandtabs())
        return ByteArray(self._value.expandtabs(size))

    def find(
        self,
        sub: ByteArray,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return Int(
            self._value.find(_faithful(sub), _unwrap(start, None), _unwrap(end, None))
        )

    def index(
        self,
        sub: ByteArray,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return Int(
            self._value.index(_faithful(sub), _unwrap(start, None), _unwrap(end, None))
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

    def join(self, parts: List) -> ByteArray:
        # Mirror CPython: unwrap each element to its underlying value and let
        # bytearray.join validate. Bytes-like POOP wrappers (Bytes/ByteArray/
        # MemoryView) join cleanly; anything else (Str, Int, ...) reaches
        # bytearray.join unwrapped and raises the faithful TypeError instead
        # of being silently dropped.
        pieces: list[Any] = [_faithful(p) for p in parts]
        return ByteArray(self._value.join(pieces))

    def ljust(
        self,
        width: Int,
        fillchar: ByteArray | NoneClass | None = None,
    ) -> ByteArray:

        fill = _unwrap(fillchar, None)
        if fill is None:
            return ByteArray(self._value.ljust(_faithful(width)))
        return ByteArray(self._value.ljust(_faithful(width), bytes(fill)))

    def lower(self) -> ByteArray:
        return ByteArray(self._value.lower())

    def lstrip(self, chars: ByteArray | NoneClass | None = None) -> ByteArray:

        return ByteArray(self._value.lstrip(_unwrap(chars, None)))

    def partition(self, sep: ByteArray) -> Tuple:
        return Tuple(*[ByteArray(p) for p in self._value.partition(_faithful(sep))])

    def removeprefix(self, prefix: ByteArray) -> ByteArray:
        return ByteArray(self._value.removeprefix(bytes(_faithful(prefix))))

    def removesuffix(self, suffix: ByteArray) -> ByteArray:
        return ByteArray(self._value.removesuffix(bytes(_faithful(suffix))))

    def replace(
        self,
        old: ByteArray,
        new: ByteArray,
        count: Int | NoneClass | None = None,
    ) -> ByteArray:
        return ByteArray(
            self._value.replace(
                _faithful(old),
                _faithful(new),
                _unwrap(count, -1),
            )
        )

    def rfind(
        self,
        sub: ByteArray,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return Int(
            self._value.rfind(_faithful(sub), _unwrap(start, None), _unwrap(end, None))
        )

    def rindex(
        self,
        sub: ByteArray,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return Int(
            self._value.rindex(_faithful(sub), _unwrap(start, None), _unwrap(end, None))
        )

    def rjust(
        self,
        width: Int,
        fillchar: ByteArray | NoneClass | None = None,
    ) -> ByteArray:

        fill = _unwrap(fillchar, None)
        if fill is None:
            return ByteArray(self._value.rjust(_faithful(width)))
        return ByteArray(self._value.rjust(_faithful(width), bytes(fill)))

    def rpartition(self, sep: ByteArray) -> Tuple:
        return Tuple(*[ByteArray(p) for p in self._value.rpartition(_faithful(sep))])

    def rsplit(
        self,
        sep: ByteArray | NoneClass | None = None,
        maxsplit: Int | NoneClass | None = None,
    ) -> List:
        return List(
            *[
                ByteArray(p)
                for p in self._value.rsplit(_unwrap(sep, None), _unwrap(maxsplit, -1))
            ]
        )

    def rstrip(self, chars: ByteArray | NoneClass | None = None) -> ByteArray:

        return ByteArray(self._value.rstrip(_unwrap(chars, None)))

    def split(
        self,
        sep: ByteArray | NoneClass | None = None,
        maxsplit: Int | NoneClass | None = None,
    ) -> List:
        return List(
            *[
                ByteArray(p)
                for p in self._value.split(_unwrap(sep, None), _unwrap(maxsplit, -1))
            ]
        )

    def splitlines(self, keepends: Boolean | NoneClass | None = None) -> List:
        from poop.types._unwrap import _unwrap_bool

        return List(
            *[
                ByteArray(p)
                for p in self._value.splitlines(_unwrap_bool(keepends, False))
            ]
        )

    def startswith(
        self,
        prefix: ByteArray,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return (
            true
            if self._value.startswith(
                bytes(_faithful(prefix)),
                _unwrap(start, None),
                _unwrap(end, None),
            )
            else false
        )

    def strip(self, chars: ByteArray | NoneClass | None = None) -> ByteArray:

        return ByteArray(self._value.strip(_unwrap(chars, None)))

    def swapcase(self) -> ByteArray:
        return ByteArray(self._value.swapcase())

    def title(self) -> ByteArray:
        return ByteArray(self._value.title())

    def upper(self) -> ByteArray:
        return ByteArray(self._value.upper())

    def zfill(self, width: Int) -> ByteArray:
        return ByteArray(self._value.zfill(_faithful(width)))

    def __str__(self) -> str:
        return repr(self._value)

    __repr__ = __str__


ByteArray.__module__ = "builtins"
ByteArray.__name__ = "bytearray"
