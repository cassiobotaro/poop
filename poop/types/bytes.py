from typing import TYPE_CHECKING, ClassVar

from poop.types._bytes_like import _BytesLikeMixin, _from_hex
from poop.types._iterable_mixin import _IterableMixin
from poop.types._ordered import _OrderedMixin
from poop.types._value_eq import _ValueEqMixin
from poop.types.byte_array import ByteArray
from poop.types.bytes_iterator import BytesIterator
from poop.types.int import Int
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.string import Str


class Bytes(
    _BytesLikeMixin["Bytes"],
    _OrderedMixin,
    _ValueEqMixin,
    _IterableMixin[Int],
    Object,
    name="bytes",
):
    __slots__ = ("_value",)
    _value: bytes
    _eq_attr: ClassVar[str] = "_value"
    _eq_group: ClassVar[str | None] = "bytes"
    _order_group: ClassVar[str | None] = "bytes"

    def __init__(self, value: bytes | Bytes) -> None:
        self._value = value._value if isinstance(value, Bytes) else value

    def _rewrap(self, raw: bytes | bytearray) -> Bytes:
        # `bytes(raw)` is `raw` itself for a `bytes` — which is all this
        # receiver's payload ever answers — and the copy a `bytearray` needs.
        return Bytes(bytes(raw))

    @classmethod
    def fromhex(cls, s: Str) -> Bytes:
        return _from_hex(cls, bytes, s)

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
