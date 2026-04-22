from collections import deque
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.list import List

_memoryview = memoryview  # alias to avoid shadowing by MemoryView class name


class MemoryView(Object):
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

        item = self._value[index._value]
        # memoryview of bytes/bytearray yields int items
        return Int(item if isinstance(item, int) else item)

    def __getitem__(self, index: Int) -> Int:
        return self.at(index)

    def for_each(self, block: Callable[[Int], Any]) -> None:
        from poop.types.int import Int

        deque((block(Int(b)) for b in self._value), maxlen=0)

    def map(self, block: Callable[[Int], Any]) -> List:
        from poop.types.int import Int
        from poop.types.list import List

        return List(*(block(Int(b)) for b in self._value))

    def __iter__(self) -> Iterator[Int]:
        from poop.types.int import Int

        return (Int(b) for b in self._value)

    def tobytes(self) -> bytes:
        return self._value.tobytes()

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
