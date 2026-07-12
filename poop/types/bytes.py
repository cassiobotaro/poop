import base64 as _base64
import hashlib as _hashlib
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._iterable_mixin import _IterableMixin
from poop.types._unwrap import _is_absent, _unwrap
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import Boolean, false, to_boolean, true
from poop.types.bytes_iterator import BytesIterator
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.hash import Hash
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.none import NoneClass
    from poop.types.slice import Slice
    from poop.types.string import Str
    from poop.types.tuple import Tuple

_bytes = bytes  # alias to avoid shadowing by Bytes class name in annotations


def _repeat_count(other: object) -> Any:
    """Repeat count for sequence multiplication, folding ``Boolean`` to 1/0.

    ``bool`` is an ``int`` subclass — ``b"ab" * True == b"ab"`` — but a POOP
    ``Boolean`` has no ``_value`` slot, so fold it explicitly. Any other operand
    is unwrapped to its underlying value (or passed through) so ``bytes.__mul__``
    raises CPython's faithful ``can't multiply sequence by non-int`` ``TypeError``
    for non-integers.
    """
    from poop.types.boolean import Boolean

    if isinstance(other, Boolean):
        return int(bool(other))
    return getattr(other, "_value", other)


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
        from poop.types._unwrap import _is_absent, _opt_int
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

    # base64 — encoders. Each returns Bytes (ASCII-bearing), mirroring
    # Python's base64.<name>(b) which always returns bytes.

    def b16encode(self) -> Bytes:
        return Bytes(_base64.b16encode(self._value))

    def b32encode(self) -> Bytes:
        return Bytes(_base64.b32encode(self._value))

    def b32hexencode(self) -> Bytes:
        return Bytes(_base64.b32hexencode(self._value))

    def b64encode(self, altchars: Bytes | NoneClass | None = None) -> Bytes:
        kwargs: dict[str, _bytes] = {}
        if not _is_absent(altchars):
            kwargs["altchars"] = altchars._value
        return Bytes(_base64.b64encode(self._value, **kwargs))

    def standard_b64encode(self) -> Bytes:
        return Bytes(_base64.standard_b64encode(self._value))

    def urlsafe_b64encode(self) -> Bytes:
        return Bytes(_base64.urlsafe_b64encode(self._value))

    def a85encode(
        self,
        *,
        foldspaces: Boolean | NoneClass | None = None,
        wrapcol: Int | None = None,
        pad: Boolean | NoneClass | None = None,
        adobe: Boolean | NoneClass | None = None,
    ) -> Bytes:
        from typing import Any as _Any

        kwargs: dict[str, _Any] = {}
        if not _is_absent(foldspaces):
            kwargs["foldspaces"] = bool(foldspaces)
        if not _is_absent(wrapcol):
            kwargs["wrapcol"] = wrapcol._value
        if not _is_absent(pad):
            kwargs["pad"] = bool(pad)
        if not _is_absent(adobe):
            kwargs["adobe"] = bool(adobe)
        return Bytes(_base64.a85encode(self._value, **kwargs))

    def b85encode(self, pad: Boolean | NoneClass | None = None) -> Bytes:
        if _is_absent(pad):
            return Bytes(_base64.b85encode(self._value))
        return Bytes(_base64.b85encode(self._value, pad=bool(pad)))

    def z85encode(self) -> Bytes:
        return Bytes(_base64.z85encode(self._value))

    # base64 — decoders on Bytes. Each returns Bytes.

    def b16decode(self, casefold: Boolean | NoneClass | None = None) -> Bytes:
        if _is_absent(casefold):
            return Bytes(_base64.b16decode(self._value))
        return Bytes(_base64.b16decode(self._value, casefold=bool(casefold)))

    def b32decode(
        self,
        casefold: Boolean | NoneClass | None = None,
        map01: Bytes | NoneClass | None = None,
    ) -> Bytes:
        from typing import Any as _Any

        kwargs: dict[str, _Any] = {}
        if not _is_absent(casefold):
            kwargs["casefold"] = bool(casefold)
        if not _is_absent(map01):
            kwargs["map01"] = map01._value
        return Bytes(_base64.b32decode(self._value, **kwargs))

    def b32hexdecode(self, casefold: Boolean | NoneClass | None = None) -> Bytes:
        if _is_absent(casefold):
            return Bytes(_base64.b32hexdecode(self._value))
        return Bytes(_base64.b32hexdecode(self._value, casefold=bool(casefold)))

    def b64decode(
        self,
        altchars: Bytes | NoneClass | None = None,
        validate: Boolean | NoneClass | None = None,
    ) -> Bytes:
        from typing import Any as _Any

        kwargs: dict[str, _Any] = {}
        if not _is_absent(altchars):
            kwargs["altchars"] = altchars._value
        if not _is_absent(validate):
            kwargs["validate"] = bool(validate)
        return Bytes(_base64.b64decode(self._value, **kwargs))

    def standard_b64decode(self) -> Bytes:
        return Bytes(_base64.standard_b64decode(self._value))

    def urlsafe_b64decode(self) -> Bytes:
        return Bytes(_base64.urlsafe_b64decode(self._value))

    def a85decode(
        self,
        foldspaces: Boolean | NoneClass | None = None,
        adobe: Boolean | NoneClass | None = None,
        ignorechars: Bytes | NoneClass | None = None,
    ) -> Bytes:
        from typing import Any as _Any

        kwargs: dict[str, _Any] = {}
        if not _is_absent(foldspaces):
            kwargs["foldspaces"] = bool(foldspaces)
        if not _is_absent(adobe):
            kwargs["adobe"] = bool(adobe)
        if not _is_absent(ignorechars):
            kwargs["ignorechars"] = ignorechars._value
        return Bytes(_base64.a85decode(self._value, **kwargs))

    def b85decode(self) -> Bytes:
        return Bytes(_base64.b85decode(self._value))

    def z85decode(self) -> Bytes:
        return Bytes(_base64.z85decode(self._value))

    # hashlib — shortcut messages. Each returns a POOP `Hash` wrapping
    # the corresponding Python hashlib hash object. Mirrors
    # `hashlib.<algo>(b)` exactly.

    def md5(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.md5(self._value))  # noqa: S324

    def sha1(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.sha1(self._value))  # noqa: S324

    def sha224(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.sha224(self._value))

    def sha256(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.sha256(self._value))

    def sha384(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.sha384(self._value))

    def sha512(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.sha512(self._value))

    def blake2b(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.blake2b(self._value))

    def blake2s(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.blake2s(self._value))

    def sha3_224(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.sha3_224(self._value))

    def sha3_256(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.sha3_256(self._value))

    def sha3_384(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.sha3_384(self._value))

    def sha3_512(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.sha3_512(self._value))

    def shake_128(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.shake_128(self._value))

    def shake_256(self) -> Hash:
        from poop.types.hash import Hash

        return Hash(_hashlib.shake_256(self._value))

    # hashlib — key-derivation functions. Receiver is the password
    # (substituting Python's first positional argument).

    def pbkdf2_hmac(
        self,
        hash_name: Str,
        salt: Bytes,
        iterations: Int,
        dklen: Int | NoneClass | None = None,
    ) -> Bytes:

        length = _unwrap(dklen, None)
        return Bytes(
            _hashlib.pbkdf2_hmac(
                hash_name._value,
                self._value,
                salt._value,
                iterations._value,
                length,
            )
        )

    def scrypt(
        self,
        *,
        salt: Bytes,
        n: Int,
        r: Int,
        p: Int,
        maxmem: Int | NoneClass | None = None,
        dklen: Int | NoneClass | None = None,
    ) -> Bytes:

        return Bytes(
            _hashlib.scrypt(
                self._value,
                salt=salt._value,
                n=n._value,
                r=r._value,
                p=p._value,
                maxmem=_unwrap(maxmem, 0),
                dklen=_unwrap(dklen, 64),
            )
        )

    def __str__(self) -> str:
        return repr(self._value)

    __repr__ = __str__


Bytes.__module__ = "builtins"
Bytes.__name__ = "bytes"
