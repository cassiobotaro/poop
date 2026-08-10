from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._affix import affix_needle
from poop.types._argument import a_bound, text_like
from poop.types._at import at_index
from poop.types._cloak import cloak
from poop.types._codec import decoded
from poop.types._iterable_mixin import _IterableMixin
from poop.types._repeat import _repeat_count
from poop.types._unwrap import _faithful, _is_absent, _unwrap
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import Boolean, false, to_boolean, true
from poop.types.byte_array import ByteArray
from poop.types.bytes_iterator import BytesIterator
from poop.types.exceptions import MIRRORS
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types._index import Index
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

    def at(self, index: Index) -> Int:
        from poop.types.int import Int

        return Int(at_index(self._value, index, self))

    def slice(
        self,
        start_or_slice: Index | Slice | NoneClass | None,
        stop: Index | NoneClass | None = None,
        step: Index | NoneClass | None = None,
    ) -> Bytes:
        from poop.types.slice import _resolve_py_slice

        py = _resolve_py_slice(start_or_slice, stop, step)
        return Bytes(self._value[py])

    def includes(self, byte: Int) -> Boolean:
        # getattr-unwrap (as in join): a non-`_value` argument (List, Set, …)
        # reaches bytes.__contains__ raw and raises the faithful TypeError,
        # rather than leaking the internal `_value` name through dispatch. A
        # Bytes/ByteArray argument keeps its subsequence-membership semantics.
        operand: Any = _faithful(byte)
        return to_boolean(operand in self._value)

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
            decoded(
                self._value,
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
        sep_value = text_like(sep, "hex", "a one-character separator")
        return Str(self._value.hex(sep_value, _opt_int(bytes_per_sep, 1)))

    @classmethod
    def fromhex(cls, s: Str) -> Bytes:
        # CPython answers `non-hexadecimal number found in fromhex() arg at
        # position 0` — the message spelt as a call, with an argument index
        # for a message that takes exactly one.
        try:
            return cls(bytes.fromhex(text_like(s, "fromhex", "a str")))
        except ValueError:
            raise MIRRORS["ValueError"](
                f"{s!r} is not hexadecimal — #fromhex reads pairs of hex digits"
            ) from None

    def __iter__(self) -> Iterator[Int]:
        from poop.types.int import Int

        return (Int(b) for b in self._value)

    def iter(self) -> BytesIterator:
        return BytesIterator(self)

    def ord(self) -> Int:
        # `no_chr` forbids `ord(x)` and names `x.ord()`. CPython's `ord` takes
        # a one-character `str` **or** a one-byte `bytes` — `ord(b"a")` is 97 —
        # and only `Str` answered the message. A receiver that is not exactly
        # one byte long is left to CPython's faithful TypeError.
        from poop.types.int import Int

        try:
            return Int(ord(self._value))
        except TypeError:
            # CPython answers `ord() expected a character, but string of
            # length 2 found`: the builtin as a call, and `string` for a
            # receiver that prints as bytes.
            raise MIRRORS["TypeError"](
                f"#ord expects a single byte, got {len(self._value)}"
            ) from None

    def reversed(self) -> Bytes:
        # `bytes` is a sequence, so `reversed(b"abc")` works in CPython and
        # `no_reversed` bans it — this is the substitute it points at. A
        # `Bytes`, like every other receiver's own kind.
        return Bytes(self._value[::-1])

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

    def __add__(self, other: object) -> Bytes:
        # Both byte-likes pass: CPython concatenates `bytes + bytearray` and
        # answers bytes. Anything else -> faithful TypeError, not #_value.
        if not isinstance(other, Bytes | ByteArray):
            return NotImplemented
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
            return Bytes(self._value.center(_faithful(width)))
        return Bytes(
            self._value.center(
                _faithful(width), text_like(fillchar, "center", "one byte")
            )
        )

    def count(
        self,
        sub: Bytes,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.count(
                _faithful(sub),
                a_bound(start, "count", "start"),
                a_bound(end, "count", "end"),
            )
        )

    def endswith(
        self,
        suffix: Bytes | Tuple,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return (
            true
            if self._value.endswith(
                affix_needle(suffix),
                a_bound(start, "endswith", "start"),
                a_bound(end, "endswith", "end"),
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
            self._value.find(
                _faithful(sub),
                a_bound(start, "find", "start"),
                a_bound(end, "find", "end"),
            )
        )

    def index(
        self,
        sub: Bytes,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.index(
                _faithful(sub),
                a_bound(start, "index", "start"),
                a_bound(end, "index", "end"),
            )
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
        pieces: list[Any] = [_faithful(p) for p in parts]
        return Bytes(self._value.join(pieces))

    def ljust(self, width: Int, fillchar: Bytes | NoneClass | None = None) -> Bytes:
        fill = _unwrap(fillchar, None)
        if fill is None:
            return Bytes(self._value.ljust(_faithful(width)))
        return Bytes(
            self._value.ljust(
                _faithful(width), text_like(fillchar, "ljust", "one byte")
            )
        )

    def lower(self) -> Bytes:
        return Bytes(self._value.lower())

    def lstrip(self, chars: Bytes | NoneClass | None = None) -> Bytes:
        return Bytes(self._value.lstrip(_unwrap(chars, None)))

    def partition(self, sep: Bytes) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*[Bytes(p) for p in self._value.partition(_faithful(sep))])

    def removeprefix(self, prefix: Bytes) -> Bytes:
        return Bytes(self._value.removeprefix(_faithful(prefix)))

    def removesuffix(self, suffix: Bytes) -> Bytes:
        return Bytes(self._value.removesuffix(_faithful(suffix)))

    def replace(
        self,
        old: Bytes,
        new: Bytes,
        count: Int | NoneClass | None = None,
    ) -> Bytes:
        return Bytes(
            self._value.replace(
                _faithful(old),
                _faithful(new),
                _unwrap(count, -1),
            )
        )

    def rfind(
        self,
        sub: Bytes,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.rfind(
                _faithful(sub),
                a_bound(start, "rfind", "start"),
                a_bound(end, "rfind", "end"),
            )
        )

    def rindex(
        self,
        sub: Bytes,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        from poop.types.int import Int

        return Int(
            self._value.rindex(
                _faithful(sub),
                a_bound(start, "rindex", "start"),
                a_bound(end, "rindex", "end"),
            )
        )

    def rjust(self, width: Int, fillchar: Bytes | NoneClass | None = None) -> Bytes:
        fill = _unwrap(fillchar, None)
        if fill is None:
            return Bytes(self._value.rjust(_faithful(width)))
        return Bytes(
            self._value.rjust(
                _faithful(width), text_like(fillchar, "rjust", "one byte")
            )
        )

    def rpartition(self, sep: Bytes) -> Tuple:
        from poop.types.tuple import Tuple

        return Tuple(*[Bytes(p) for p in self._value.rpartition(_faithful(sep))])

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
        prefix: Bytes | Tuple,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return (
            true
            if self._value.startswith(
                affix_needle(prefix),
                a_bound(start, "startswith", "start"),
                a_bound(end, "startswith", "end"),
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
        return Bytes(self._value.zfill(_faithful(width)))

    def __str__(self) -> str:
        return repr(self._value)

    __repr__ = __str__


cloak(Bytes, "bytes")
