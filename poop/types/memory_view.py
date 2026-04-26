from collections import deque
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.bytes import Bytes
    from poop.types.int import Int
    from poop.types.list import List

_memoryview = memoryview  # alias to avoid shadowing by MemoryView class name


class MemoryView(_IterableMixin, Object):
    __slots__ = ("_value",)

    def __init__(self, value: _memoryview) -> None:
        self._value = value

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._value))

    def __len__(self) -> int:
        return len(self._value)

    def at(self, index: Int) -> Int:
        from poop.types.int import Int

        return Int(self._value[index._value])

    def __iter__(self) -> Iterator[Int]:
        from poop.types.int import Int

        return (Int(b) for b in self._value)

    def tobytes(self) -> Bytes:
        from poop.types.bytes import Bytes

        return Bytes(self._value.tobytes())

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, MemoryView):
            return true if self._value == other._value else false
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, MemoryView):
            return false if self._value == other._value else true
        return true

    def __str__(self) -> str:
        return repr(self._value)

    __repr__ = __str__
