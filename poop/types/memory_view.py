from collections.abc import Iterator
from typing import TYPE_CHECKING, ClassVar, Literal, cast

from poop.types._iterable_mixin import _IterableMixin
from poop.types._value_eq import _ValueEqMixin
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.memory_view_iterator import MemoryViewIterator
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.none import NoneClass
    from poop.types.string import Str

_memoryview = memoryview  # alias to avoid shadowing by MemoryView class name


class MemoryView(_ValueEqMixin, _IterableMixin, Object):
    __slots__ = ("_value",)
    _eq_attr: ClassVar[str] = "_value"
    # CPython compares memoryview equal by value to bytes/bytearray (and
    # other memoryviews): `memoryview(b"abc") == b"abc"` is True. Share the
    # "bytes" group so the same holds in POOP.
    _eq_group: ClassVar[str] = "bytes"

    def __init__(self, value: _memoryview | MemoryView) -> None:
        self._value = value._value if isinstance(value, MemoryView) else value

    def __hash__(self) -> int:
        # Mirror CPython: a memoryview is hashable iff it is read-only and of
        # byte format, and then hashes equal to the underlying bytes. Keeping
        # this in sync with the "bytes" eq group preserves the eq/hash
        # invariant against Bytes.
        return hash(self._value)

    def len(self) -> Int:
        return Int(len(self._value))

    def __len__(self) -> int:
        return len(self._value)

    def at(self, index: Int) -> Int:
        return Int(self._value[index._value])

    def __iter__(self) -> Iterator[Int]:
        return (Int(b) for b in self._value)

    def iter(self) -> MemoryViewIterator:
        return MemoryViewIterator(self)

    def tobytes(self, order: Str | NoneClass | None = None) -> Bytes:
        from poop.types._unwrap import _unwrap

        return Bytes(
            self._value.tobytes(cast(Literal["C", "F", "A"], _unwrap(order, "C")))
        )

    def __str__(self) -> str:
        return repr(self._value)

    __repr__ = __str__


MemoryView.__module__ = "builtins"
MemoryView.__name__ = "memoryview"
