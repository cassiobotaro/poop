"""What `bytes` and `bytearray` answer alike, written once.

The two wrappers mirror each other message for message, and keeping a mirror
by hand had already cost twice: the text form was a half-pair, present on
`bytes` and missing on `bytearray`, and the comparisons had to be fixed in two
classes, four methods each. CPython shares the same code between the two
(`bytes_methods.c`); this is that file's place here.

Each concrete class supplies `_rewrap`, which turns a raw result back into its
own kind — a `Bytes` answers a `Bytes`, a `ByteArray` a `ByteArray` — and keeps
what differs: construction, `+`, `fromhex`, hashing, the iterator it hands
out and, on `ByteArray`, the mutators.
"""

from typing import TYPE_CHECKING

from poop.types import mirrors
from poop.types._affix import affix_needle
from poop.types._argument import (
    a_bound,
    a_collection,
    a_fill,
    a_needle,
    an_int,
    bytes_like,
    max_split,
    text_like,
)
from poop.types._at import at_index
from poop.types._codec import decoded
from poop.types._mixin import _Mixin
from poop.types._repeat import _repeat_count
from poop.types._sentinel import NOT_A_COUNT
from poop.types._unwrap import _is_absent, _unwrap, _unwrap_bool
from poop.types.boolean import to_boolean
from poop.types.int import Int
from poop.types.list import List
from poop.types.object import Object
from poop.types.slice import _resolve_py_slice
from poop.types.string import Str
from poop.types.tuple import Tuple

# circular: bytes imports _bytes_like
lazy from poop.types.bytes import Bytes

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from poop.types._index import Index
    from poop.types.boolean import Boolean
    from poop.types.byte_array import ByteArray
    from poop.types.none import NoneClass
    from poop.types.slice import Slice

    type BytesLike = Bytes | ByteArray


_BYTE_KINDS = (bytes, bytearray, memoryview)


def hex_of(
    value: bytes | bytearray | memoryview,
    sep: Str | Bytes | NoneClass | None,
    bytes_per_sep: Int | NoneClass | None,
) -> Str:
    """`value.hex(sep, bytes_per_sep)`, the separator guarded in POOP's words.

    One body for the three receivers that answer `hex`: the two byte wrappers
    through the mixin, `MemoryView` by calling this. Three copies had drifted —
    `bytearray` passed no kinds to the guard and then converted a `bytearray`
    separator, so it accepted what `bytes` refused and what CPython refuses on
    both (`sep must be str or bytes`).
    """
    if _is_absent(sep):
        return Str(value.hex())
    sep_value = text_like(sep, "hex", "a one-character separator", (str, bytes))
    return Str(value.hex(sep_value, an_int(bytes_per_sep, "hex", "bytes_per_sep", 1)))


class _BytesLikeMixin[B: Object](_Mixin, name="bytes"):
    __slots__ = ()  # empty, as `_Mixin` says every mixin's must be

    _value: bytes | bytearray

    def _rewrap(self, raw: bytes | bytearray) -> B:
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

    def hex(
        self,
        sep: Str | Bytes | NoneClass | None = None,
        bytes_per_sep: Int | NoneClass | None = None,
    ) -> Str:
        return hex_of(self._value, sep, bytes_per_sep)

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
        # `a_needle` admits a byte-like or an int and refuses anything else
        # (List, Set, …) in `includes`'s name, so the internal `_value` never
        # shows through dispatch. A Bytes/ByteArray argument keeps its
        # subsequence-membership semantics.
        operand = a_needle(self, byte, "includes", "bytes or an int", _BYTE_KINDS)
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
                _unwrap(encoding, "utf-8"),
                _unwrap(errors, "strict"),
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
            raise mirrors.TypeError(
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

    def _fill(self, fillchar: object, selector: str) -> bytes | None:
        """The optional fill of `center` / `ljust` / `rjust`, as `bytes`.

        CPython takes a `bytearray` fill too; typeshed spells the parameter
        `bytes` alone, and `bytes(fill)` is `fill` itself for a `bytes`.
        """
        fill = a_fill(fillchar, selector, "one byte", (bytes, bytearray))
        return None if fill is None else bytes(fill)

    def _pad(
        self,
        method: Callable[..., bytes | bytearray],
        selector: str,
        width: Int,
        fillchar: object,
    ) -> B:
        """`center` and its two siblings: one guarded call to the native method."""
        w = an_int(width, selector, "width")
        fill = self._fill(fillchar, selector)
        return self._rewrap(method(w) if fill is None else method(w, fill))

    def center(self, width: Int, fillchar: BytesLike | NoneClass | None = None) -> B:
        return self._pad(self._value.center, "center", width, fillchar)

    def _search(
        self,
        method: Callable[..., int],
        selector: str,
        sub: object,
        start: Int | NoneClass | None,
        end: Int | NoneClass | None,
    ) -> Int:
        """`find` and its four siblings: one guarded call to the native method.

        The bound method rather than a name to `getattr`, so a misspelt
        selector cannot reach the wrong native method.
        """
        return Int(
            method(
                a_needle(self, sub, selector, "bytes or an int", _BYTE_KINDS),
                a_bound(start, selector, "start"),
                a_bound(end, selector, "end"),
            )
        )

    def _affix(
        self,
        method: Callable[..., bool],
        selector: str,
        affix: object,
        start: Int | NoneClass | None,
        end: Int | NoneClass | None,
    ) -> Boolean:
        """`startswith` / `endswith`, guarded the way `_search` is."""
        return to_boolean(
            method(
                affix_needle(affix, selector, "bytes or a tuple of bytes", _BYTE_KINDS),
                a_bound(start, selector, "start"),
                a_bound(end, selector, "end"),
            )
        )

    def count(
        self,
        sub: BytesLike | Int,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return self._search(self._value.count, "count", sub, start, end)

    def endswith(
        self,
        suffix: BytesLike | Tuple,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Boolean:
        return self._affix(self._value.endswith, "endswith", suffix, start, end)

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
        return self._search(self._value.find, "find", sub, start, end)

    def index(
        self,
        sub: BytesLike | Int,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return self._search(self._value.index, "index", sub, start, end)

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
        # `bytes_like` unwraps each byte-like element (Bytes/ByteArray/
        # MemoryView) for the native join and refuses anything else (Str,
        # Int, ...) in `join`'s name, where CPython names a `sequence item`.
        pieces = [bytes_like(p, "join") for p in a_collection(parts, "join")]
        return self._rewrap(self._value.join(pieces))

    def ljust(self, width: Int, fillchar: BytesLike | NoneClass | None = None) -> B:
        return self._pad(self._value.ljust, "ljust", width, fillchar)

    def lower(self) -> B:
        return self._rewrap(self._value.lower())

    @staticmethod
    def maketrans(frm: BytesLike, to: BytesLike) -> Bytes:
        """`bytes.maketrans`: the 256-byte table `translate` reads.

        Static, as CPython's is, and answering `bytes` from both classes —
        `bytearray.maketrans(b"a", b"b")` is a `bytes` in CPython — which is
        why it lives here rather than once per class like `fromhex`. Unequal
        lengths keep CPython's `maketrans arguments must have same length`,
        which names no construct POOP forbids; a `str` argument reached
        `a bytes-like object is required, not 'str'`, and `bytes_like` words
        it.
        """
        return Bytes(
            bytes.maketrans(bytes_like(frm, "maketrans"), bytes_like(to, "maketrans"))
        )

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
                an_int(count, "replace", "count", -1),
            )
        )

    def rfind(
        self,
        sub: BytesLike | Int,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return self._search(self._value.rfind, "rfind", sub, start, end)

    def rindex(
        self,
        sub: BytesLike | Int,
        start: Int | NoneClass | None = None,
        end: Int | NoneClass | None = None,
    ) -> Int:
        return self._search(self._value.rindex, "rindex", sub, start, end)

    def rjust(self, width: Int, fillchar: BytesLike | NoneClass | None = None) -> B:
        return self._pad(self._value.rjust, "rjust", width, fillchar)

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
        return self._affix(self._value.startswith, "startswith", prefix, start, end)

    def strip(self, chars: BytesLike | NoneClass | None = None) -> B:
        return self._rewrap(
            self._value.strip(bytes_like(chars, "strip", optional=True))
        )

    def swapcase(self) -> B:
        return self._rewrap(self._value.swapcase())

    def title(self) -> B:
        return self._rewrap(self._value.title())

    def translate(
        self,
        table: BytesLike | NoneClass | None,
        delete: BytesLike | NoneClass | None = None,
    ) -> B:
        """`bytes.translate`: every byte through `table`, minus `delete`.

        `table` may be `none`, which deletes without mapping; `delete` is
        empty by default. A table that is not 256 bytes long keeps CPython's
        `translation table must be 256 characters long`.
        """
        deleted = bytes_like(delete, "translate", optional=True)
        # `bytes(deleted)`, as `_fill` does: typeshed spells `bytearray`'s
        # `delete` as `bytes` alone, and the copy is free for a `bytes`.
        return self._rewrap(
            self._value.translate(
                bytes_like(table, "translate", optional=True),
                b"" if deleted is None else bytes(deleted),
            )
        )

    def upper(self) -> B:
        return self._rewrap(self._value.upper())

    def zfill(self, width: Int) -> B:
        return self._rewrap(self._value.zfill(an_int(width, "zfill", "width")))

    def __str__(self) -> str:
        return repr(self._value)
