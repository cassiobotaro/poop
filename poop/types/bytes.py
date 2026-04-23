from collections import deque
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.string import Str

_bytes = bytes  # alias to avoid shadowing by Bytes class name in annotations


class Bytes(Object):
    __slots__ = ("_value",)

    def __init__(self, value: _bytes) -> None:
        self._value = value

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._value))

    def __len__(self) -> int:
        return len(self._value)

    def at(self, index: Int) -> Int:
        from poop.types.int import Int

        return Int(self._value[index._value])

    def __getitem__(self, index: Int) -> Int:
        return self.at(index)

    def includes(self, byte: Int) -> Boolean:
        from poop.types.boolean import false, true

        return true if byte._value in self._value else false

    def __contains__(self, item: object) -> bool:
        from poop.types.int import Int

        if isinstance(item, Int):
            return item._value in self._value
        return False

    def decode(self, encoding: Str) -> Str:
        from poop.types.string import Str

        return Str(self._value.decode(encoding._value))

    def hex(self) -> Str:
        from poop.types.string import Str

        return Str(self._value.hex())

    def do(self, block: Callable[[Int], Any]) -> None:
        from poop.types.int import Int

        deque((block(Int(b)) for b in self._value), maxlen=0)

    def map(self, block: Callable[[Int], Any]) -> List:
        from poop.types.int import Int
        from poop.types.list import List

        return List(*(block(Int(b)) for b in self._value))

    def __iter__(self) -> Iterator[Int]:
        from poop.types.int import Int

        return (Int(b) for b in self._value)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Bytes):
            return true if self._value == other._value else false
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Bytes):
            return false if self._value == other._value else true
        return true

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return repr(self._value)

    __repr__ = __str__
