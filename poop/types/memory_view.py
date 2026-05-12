from collections.abc import Iterator
from typing import ClassVar

from poop.types._iterable_mixin import _IterableMixin
from poop.types._value_eq import _ValueEqMixin
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.memory_view_iterator import MemoryViewIterator
from poop.types.object import Object

_memoryview = memoryview  # alias to avoid shadowing by MemoryView class name


class MemoryView(_ValueEqMixin, _IterableMixin, Object):
    __slots__ = ("_value",)
    _eq_attr: ClassVar[str] = "_value"

    def __init__(self, value: _memoryview | MemoryView) -> None:
        self._value = value._value if isinstance(value, MemoryView) else value

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

    def tobytes(self) -> Bytes:
        return Bytes(self._value.tobytes())

    def __str__(self) -> str:
        return repr(self._value)

    __repr__ = __str__


MemoryView.__module__ = "builtins"
MemoryView.__name__ = "memoryview"
