from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._alias import wrapped_instance
from poop.types._argument import a_collection, an_int, text_like
from poop.types._at import (
    no_element_at,
    no_element_equal_to,
    nothing_to_remove,
)
from poop.types._bytes_like import _BytesLikeMixin
from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin
from poop.types._message import article
from poop.types._ordered import _OrderedMixin
from poop.types._unwrap import (
    _faithful,
    _is_absent,
)
from poop.types._value_eq import _ValueEqMixin
from poop.types.byte_array_iterator import ByteArrayIterator
from poop.types.exceptions import MIRRORS
from poop.types.int import Int
from poop.types.none import none
from poop.types.object import Object
from poop.types.string import Str

if TYPE_CHECKING:
    from collections.abc import Iterable

    from poop.types._index import Index
    from poop.types.bytes import Bytes
    from poop.types.none import NoneClass

_bytearray = bytearray  # alias to avoid shadowing by ByteArray class name


class ByteArray(
    _BytesLikeMixin["ByteArray"], _OrderedMixin, _ValueEqMixin, _IterableMixin, Object
):
    __slots__ = ("_value",)
    _value: _bytearray
    _eq_attr: ClassVar[str] = "_value"
    _eq_group: ClassVar[str] = "bytes"
    _order_group: ClassVar[str] = "bytes"
    __hash__ = None

    def __init__(
        self,
        value: _bytearray | bytes | ByteArray | Iterable[int] | None = None,
    ) -> None:
        if value is None:
            self._value = _bytearray()
        elif isinstance(value, ByteArray):
            self._value = _bytearray(value._value)
        else:
            self._value = _bytearray(value)

    def _rewrap(self, raw: Any) -> ByteArray:
        return ByteArray(raw)

    def at_put(self, index: Index, byte: Int) -> ByteArray:
        # CPython answers `bytearray indices must be integers or slices, not
        # str` — `indices` naming the subscripting `no_subscript` bans, from
        # the message that replaces it. `at` already routes through `_at`.
        try:
            self._value[index] = _faithful(byte)
        except IndexError:
            raise no_element_at(self, self._value, index) from None
        except TypeError:
            raise MIRRORS["TypeError"](
                f"{type(self).__name__}.at_put expects an int index, "
                f"got {article(type(index).__name__)}"
            ) from None
        return self

    @classmethod
    def fromhex(cls, s: Str) -> ByteArray:
        """The writable twin of `Bytes.fromhex`, which CPython has too.

        `Bytes` and `ByteArray` mirror each other message for message — `hex`
        is right above — and this was the one half-pair: `bytes.fromhex(…)`
        answered while `bytearray.fromhex(…)` answered `bytearray does not
        understand #fromhex`, for a spelling CPython supports.
        """
        try:
            return wrapped_instance(
                cls, bytearray.fromhex(text_like(s, "fromhex", "a str"))
            )
        except ValueError:
            raise MIRRORS["ValueError"](
                f"{s!r} is not hexadecimal — #fromhex reads pairs of hex digits"
            ) from None

    def hex(
        self,
        sep: Str | ByteArray | NoneClass | None = None,
        bytes_per_sep: Int | NoneClass | None = None,
    ) -> Str:
        if _is_absent(sep):
            return Str(self._value.hex())
        raw = text_like(sep, "hex", "a one-character separator")
        # CPython's hex() takes str or bytes, not bytearray, so a ByteArray
        # separator is converted — but nothing else is, or a List of Ints
        # would be silently coerced where CPython raises.
        sep_value = bytes(raw) if isinstance(raw, _bytearray) else raw
        return Str(
            self._value.hex(sep_value, an_int(bytes_per_sep, "hex", "bytes_per_sep", 1))
        )

    def iter(self) -> ByteArrayIterator:
        return ByteArrayIterator(self)

    def __add__(self, other: object) -> ByteArray:
        # Both byte-likes pass: CPython concatenates `bytearray + bytes` and
        # answers bytearray. Anything else -> faithful TypeError, not #_value.
        # circular: bytes imports byte_array
        from poop.types.bytes import Bytes  # noqa: PLC0415

        if not isinstance(other, (ByteArray, Bytes)):
            return NotImplemented
        return ByteArray(self._value + other._value)

    def append(self, byte: Int) -> NoneClass:
        self._value.append(an_int(byte, "append", "byte"))
        return none

    def clear(self) -> NoneClass:
        self._value.clear()
        return none

    def copy(self) -> ByteArray:
        return ByteArray(self._value)

    def take_bytes(self, n: Int | NoneClass | None = None) -> Bytes:
        """The first `n` bytes as a `Bytes`, removed from the receiver.

        Python 3.15's `bytearray.take_bytes`: all of them by default, so
        `buf.take_bytes()` replaces `bytes(buf)` followed by `buf.clear()`.
        A negative `n` counts from the end, as a slice bound does, and one
        past the size is CPython's own `IndexError` — it names no construct
        POOP forbids. A mutator with an answer, so it returns the bytes
        rather than `none`.
        """
        # circular: bytes imports byte_array
        from poop.types.bytes import Bytes  # noqa: PLC0415

        return Bytes(self._value.take_bytes(an_int(n, "take_bytes", "n", None)))

    def extend(self, iterable: Object) -> NoneClass:
        raw = _faithful(a_collection(iterable, "extend"))
        # Bytes are already bytes; anything else is a collection whose every
        # element must be one, and CPython answered for the first that was not
        # with `expected iterable of integers; got: 'str'`.
        if not isinstance(raw, (bytes, _bytearray, memoryview)):
            raw = [an_int(byte, "extend", "byte") for byte in raw]
        self._value.extend(raw)
        return none

    def insert(self, i: Index, byte: Int) -> NoneClass:
        self._value.insert(an_int(i, "insert", "index"), an_int(byte, "insert", "byte"))
        return none

    def pop(self, index: Index | NoneClass | None = None) -> Int:
        try:
            if _is_absent(index):
                return Int(self._value.pop())
            return Int(self._value.pop(an_int(index, "pop", "index")))
        except IndexError:
            # The same two sentences `List.pop` answers — `pop from empty
            # bytearray` and `pop index out of range` name the method as a
            # call and leave the receiver out of both.
            if _is_absent(index):
                raise nothing_to_remove(self, "IndexError") from None
            raise no_element_at(self, self._value, index) from None

    def remove(self, byte: Int) -> NoneClass:
        try:
            self._value.remove(an_int(byte, "remove", "byte"))
        except ValueError:
            raise no_element_equal_to(self, byte) from None
        return none

    def reverse(self) -> NoneClass:
        """Reverse this byte array in place, answering `none`.

        The twin of `reversed`, which leaves the receiver alone and answers a
        new `ByteArray` — the same pair `List.reverse` / `List.reversed` are.
        """
        self._value.reverse()
        return none


cloak(ByteArray, "bytearray")
