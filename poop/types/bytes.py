from typing import TYPE_CHECKING, ClassVar

from poop.types._alias import wrapped_instance
from poop.types._argument import an_int, text_like
from poop.types._bytes_like import _BytesLikeMixin
from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin
from poop.types._ordered import _OrderedMixin
from poop.types._unwrap import (
    _is_absent,
)
from poop.types._value_eq import _ValueEqMixin
from poop.types.byte_array import ByteArray
from poop.types.bytes_iterator import BytesIterator
from poop.types.exceptions import MIRRORS
from poop.types.object import Object
from poop.types.string import Str

if TYPE_CHECKING:
    from poop.types.int import Int
    from poop.types.none import NoneClass


class Bytes(
    _BytesLikeMixin["Bytes"], _OrderedMixin, _ValueEqMixin, _IterableMixin, Object
):
    __slots__ = ("_value",)
    _value: bytes
    _eq_attr: ClassVar[str] = "_value"
    _eq_group: ClassVar[str] = "bytes"
    _order_group: ClassVar[str] = "bytes"

    def __init__(self, value: bytes | Bytes) -> None:
        self._value = value._value if isinstance(value, Bytes) else value

    def _rewrap(self, raw: bytes | bytearray) -> Bytes:
        # `bytes(raw)` is `raw` itself for a `bytes` — which is all this
        # receiver's payload ever answers — and the copy a `bytearray` needs.
        return Bytes(bytes(raw))

    def hex(
        self,
        sep: Str | Bytes | NoneClass | None = None,
        bytes_per_sep: Int | NoneClass | None = None,
    ) -> Str:
        if _is_absent(sep):
            return Str(self._value.hex())
        sep_value = text_like(sep, "hex", "a one-character separator", (str, bytes))
        return Str(
            self._value.hex(sep_value, an_int(bytes_per_sep, "hex", "bytes_per_sep", 1))
        )

    @classmethod
    def fromhex(cls, s: Str) -> Bytes:
        # CPython answers `non-hexadecimal number found in fromhex() arg at
        # position 0` — the message spelt as a call, with an argument index
        # for a message that takes exactly one.
        try:
            return wrapped_instance(
                cls, bytes.fromhex(text_like(s, "fromhex", "a str"))
            )
        except ValueError:
            raise MIRRORS["ValueError"](
                f"{s!r} is not hexadecimal — #fromhex reads pairs of hex digits"
            ) from None

    def iter(self) -> BytesIterator:
        return BytesIterator(self)

    def __hash__(self) -> int:
        return hash(self._value)

    def __add__(self, other: object) -> Bytes:
        # Both byte-likes pass: CPython concatenates `bytes + bytearray` and
        # answers bytes. Anything else -> faithful TypeError, not #_value.
        if not isinstance(other, (Bytes, ByteArray)):
            return NotImplemented
        return Bytes(self._value + other._value)


cloak(Bytes, "bytes")
