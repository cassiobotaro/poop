"""What `bytes` and `bytearray` answer alike, written once.

The two wrappers mirror each other message for message, and keeping a mirror
by hand had already cost twice: the text form was a half-pair, present on
`bytes` and missing on `bytearray`, and the comparisons had to be fixed in two
classes, four methods each. CPython shares the same code between the two
(`bytes_methods.c`); this is that file's place here.

Each concrete class supplies `_rewrap`, which turns a raw result back into its
own kind — a `Bytes` answers a `Bytes`, a `ByteArray` a `ByteArray` — and keeps
what differs: construction, `+`, `fromhex`, `hex`, hashing, the iterator it
hands out and, on `ByteArray`, the mutators.
"""

from typing import TYPE_CHECKING, Any

from poop.types._affix import affix_needle
from poop.types._argument import (
    a_bound,
    a_collection,
    a_fill,
    a_needle,
    an_int,
    bytes_like,
    max_split,
)
from poop.types._at import at_index
from poop.types._cloak import cloak
from poop.types._codec import decoded
from poop.types._repeat import _repeat_count
from poop.types._sentinel import NOT_A_COUNT
from poop.types._unwrap import _opt_str, _unwrap, _unwrap_bool
from poop.types.boolean import false, to_boolean, true
from poop.types.exceptions import MIRRORS
from poop.types.int import Int
from poop.types.list import List
from poop.types.object import Object
from poop.types.slice import _resolve_py_slice
from poop.types.string import Str
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from collections.abc import Iterator

    from poop.types._index import Index
    from poop.types.boolean import Boolean
    from poop.types.byte_array import ByteArray
    from poop.types.bytes import Bytes
    from poop.types.none import NoneClass
    from poop.types.slice import Slice

    type BytesLike = Bytes | ByteArray


_BYTE_KINDS = (bytes, bytearray, memoryview)


class _BytesLikeMixin[B: Object]:
    # Empty, like every mixin's: a slot-less class anywhere in an MRO restores
    # the per-instance `__dict__`. `_value` is each concrete class's own slot.
    __slots__ = ()

    _value: bytes | bytearray

    def _rewrap(self, raw: Any) -> B:
        """`raw` as the receiver's own builtin kind.

        The builtin's, not `type(self)`: CPython answers `bytes` from a method
        sent to a `bytes` subclass, and so does POOP.
        """
        raise NotImplementedError

    def len(self) -> Int:
        return Int(len(self._value))

    def __len__(self) -> int:
        return len(self._value)

    def at(self, index: Index) -> Int:
        return Int(at_index(self._value, index, self))

    def slice(
        self,
        start_or_slice: Index | Slice | NoneClass | None,
        stop: Index | NoneClass | None = None,
        step: Index | NoneClass | None = None,
    ) -> B:
        py = _resolve_py_slice(start_or_slice, stop, step)
        return self._rewrap(self._value[py])

    # `| Int`: CPython searches for a subsequence *or* a byte value, and the
    # guard admits both — the annotation used to say only one of them.
    def includes(self, byte: BytesLike | Int) -> Boolean:
        # getattr-unwrap (as in join): a non-`_value` argument (List, Set, …)
        # reaches the native `__contains__` raw and raises the faithful TypeError,
        # rather than leaking the internal `_value` name through dispatch. A
        # Bytes/ByteArray argument keeps its subsequence-membership semantics.
        operand: Any = a_needle(self, byte, "includes", "bytes or an int", _BYTE_KINDS)
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
        return Str(
            decoded(
                self._value,
                _opt_str(encoding, "utf-8"),
                _opt_str(errors, "strict"),
            )
        )

    def __iter__(self) -> Iterator[Int]:
        return (Int(b) for b in self._value)

    def ord(self) -> Int:
        # `no_chr` forbids `ord(x)` and names `x.ord()`. CPython's `ord` takes
        # a one-character `str` **or** a one-byte `bytes` — `ord(b"a")` is 97 —
        # and only `Str` answered the message. A receiver that is not exactly
        # one byte long is left to CPython's faithful TypeError.
        try:
            return Int(ord(self._value))
        except TypeError:
            # CPython answers `ord() expected a character, but string of
            # length 2 found`: the builtin as a call, and `string` for a
            # receiver that prints as bytes.
            raise MIRRORS["TypeError"](
                f"#ord expects a single byte, got {len(self._value)}"
            ) from None

    def reversed(self) -> B:
        # `bytes` is a sequence, so `reversed(b"abc")` works in CPython and
        # `no_reversed` bans it — this is the substitute it points at. The
        # receiver's own kind, like every other receiver's.
        return self._rewrap(self._value[::-1])

    def __mul__(self, other: object) -> B:
        count = _repeat_count(other)
        if count is NOT_A_COUNT:
            return NotImplemented
        return self._rewrap(self._value * count)

    __rmul__ = __mul__

    def capitalize(self) -> B:
        return self._rewrap(self._value.capitalize())

    def center(self, width: Int, fillchar: BytesLike | NoneClass | None = None) -> B:
        w = an_int(width, "center", "width")
        fill = a_fill(fillchar, "center", "one byte", (bytes, bytearray))
        return self._rewrap(
            self._value.center(w) if fill is None else self._value.center(w, fill)
        )

    def count(
        self,
        sub: BytesLike | Int,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return Int(
            self._value.count(
                a_needle(self, sub, "count", "bytes or an int", _BYTE_KINDS),
                a_bound(start, "count", "start"),
                a_bound(end, "count", "end"),
            )
        )

    def endswith(
        self,
        suffix: BytesLike | Tuple,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return (
            true
            if self._value.endswith(
                affix_needle(
                    suffix, "endswith", "bytes or a tuple of bytes", _BYTE_KINDS
                ),
                a_bound(start, "endswith", "start"),
                a_bound(end, "endswith", "end"),
            )
            else false
        )

    def expandtabs(self, tabsize: Int | NoneClass | None = None) -> B:
        return self._rewrap(
            self._value.expandtabs(an_int(tabsize, "expandtabs", "tabsize", 8))
        )

    def find(
        self,
        sub: BytesLike | Int,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return Int(
            self._value.find(
                a_needle(self, sub, "find", "bytes or an int", _BYTE_KINDS),
                a_bound(start, "find", "start"),
                a_bound(end, "find", "end"),
            )
        )

    def index(
        self,
        sub: BytesLike | Int,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return Int(
            self._value.index(
                a_needle(self, sub, "index", "bytes or an int", _BYTE_KINDS),
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

    def join(self, parts: List) -> B:
        # Mirror CPython: unwrap each element to its underlying value and let
        # the native join validate. Bytes-like POOP wrappers (Bytes/ByteArray/
        # MemoryView) join cleanly; anything else (Str, Int, ...) reaches
        # the native join unwrapped and raises the faithful TypeError instead of
        # being silently dropped.
        pieces: list[Any] = [bytes_like(p, "join") for p in a_collection(parts, "join")]
        return self._rewrap(self._value.join(pieces))

    def ljust(self, width: Int, fillchar: BytesLike | NoneClass | None = None) -> B:
        w = an_int(width, "ljust", "width")
        fill = a_fill(fillchar, "ljust", "one byte", (bytes, bytearray))
        return self._rewrap(
            self._value.ljust(w) if fill is None else self._value.ljust(w, fill)
        )

    def lower(self) -> B:
        return self._rewrap(self._value.lower())

    def lstrip(self, chars: BytesLike | NoneClass | None = None) -> B:
        return self._rewrap(
            self._value.lstrip(bytes_like(chars, "lstrip", optional=True))
        )

    def partition(self, sep: BytesLike) -> Tuple:
        return Tuple(
            *[
                self._rewrap(p)
                for p in self._value.partition(bytes_like(sep, "partition"))
            ]
        )

    def removeprefix(self, prefix: BytesLike) -> B:
        return self._rewrap(
            self._value.removeprefix(bytes_like(prefix, "removeprefix"))
        )

    def removesuffix(self, suffix: BytesLike) -> B:
        return self._rewrap(
            self._value.removesuffix(bytes_like(suffix, "removesuffix"))
        )

    def replace(
        self,
        old: BytesLike,
        new: BytesLike,
        count: Int | NoneClass | None = None,
    ) -> B:
        return self._rewrap(
            self._value.replace(
                bytes_like(old, "replace"),
                bytes_like(new, "replace"),
                _unwrap(count, -1),
            )
        )

    def rfind(
        self,
        sub: BytesLike | Int,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return Int(
            self._value.rfind(
                a_needle(self, sub, "rfind", "bytes or an int", _BYTE_KINDS),
                a_bound(start, "rfind", "start"),
                a_bound(end, "rfind", "end"),
            )
        )

    def rindex(
        self,
        sub: BytesLike | Int,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return Int(
            self._value.rindex(
                a_needle(self, sub, "rindex", "bytes or an int", _BYTE_KINDS),
                a_bound(start, "rindex", "start"),
                a_bound(end, "rindex", "end"),
            )
        )

    def rjust(self, width: Int, fillchar: BytesLike | NoneClass | None = None) -> B:
        w = an_int(width, "rjust", "width")
        fill = a_fill(fillchar, "rjust", "one byte", (bytes, bytearray))
        return self._rewrap(
            self._value.rjust(w) if fill is None else self._value.rjust(w, fill)
        )

    def rpartition(self, sep: BytesLike) -> Tuple:
        return Tuple(
            *[
                self._rewrap(p)
                for p in self._value.rpartition(bytes_like(sep, "rpartition"))
            ]
        )

    def rsplit(
        self,
        sep: BytesLike | NoneClass | None = None,
        maxsplit: Int | NoneClass | None = None,
    ) -> List:
        return List(
            *[
                self._rewrap(p)
                for p in self._value.rsplit(
                    bytes_like(sep, "rsplit", optional=True),
                    max_split(maxsplit, "rsplit"),
                )
            ]
        )

    def rstrip(self, chars: BytesLike | NoneClass | None = None) -> B:
        return self._rewrap(
            self._value.rstrip(bytes_like(chars, "rstrip", optional=True))
        )

    def split(
        self,
        sep: BytesLike | NoneClass | None = None,
        maxsplit: Int | NoneClass | None = None,
    ) -> List:
        return List(
            *[
                self._rewrap(p)
                for p in self._value.split(
                    bytes_like(sep, "split", optional=True),
                    max_split(maxsplit, "split"),
                )
            ]
        )

    def splitlines(self, keepends: Boolean | NoneClass | None = None) -> List:
        return List(
            *[
                self._rewrap(p)
                for p in self._value.splitlines(_unwrap_bool(keepends, False))
            ]
        )

    def startswith(
        self,
        prefix: BytesLike | Tuple,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return (
            true
            if self._value.startswith(
                affix_needle(
                    prefix, "startswith", "bytes or a tuple of bytes", _BYTE_KINDS
                ),
                a_bound(start, "startswith", "start"),
                a_bound(end, "startswith", "end"),
            )
            else false
        )

    def strip(self, chars: BytesLike | NoneClass | None = None) -> B:
        return self._rewrap(
            self._value.strip(bytes_like(chars, "strip", optional=True))
        )

    def swapcase(self) -> B:
        return self._rewrap(self._value.swapcase())

    def title(self) -> B:
        return self._rewrap(self._value.title())

    def upper(self) -> B:
        return self._rewrap(self._value.upper())

    def zfill(self, width: Int) -> B:
        return self._rewrap(self._value.zfill(an_int(width, "zfill", "width")))

    def __str__(self) -> str:
        return repr(self._value)

    __repr__ = __str__


# Cloaked as `bytes`, not `object` as the other shared mixins are: CPython
# builds a wrong-arity message from the function's qualname, so this name is
# what `b"a".upper(1)` blames. `bytes` is true for one receiver and close for
# the other — the pair is already one group under that name in `_eq_group`
# and `_order_group` — where `object` is true for neither.
cloak(_BytesLikeMixin, "bytes")
