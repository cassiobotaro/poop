from collections import deque
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.none import NoneClass
    from poop.types.tuple import Tuple

_dict = dict  # alias to avoid shadowing by Dict class name in annotations


class Dict(Object):
    __slots__ = ("_data",)

    def __init__(self) -> None:
        self._data: _dict[Object, Object] = {}

    def at(self, key: Object) -> Object | NoneClass:
        from poop.types.none import none

        return self._data.get(key, none)

    def at_put(self, key: Object, val: Object) -> Dict:
        self._data[key] = val
        return self

    def includes_key(self, key: Object) -> Boolean:
        from poop.types.boolean import false, true

        return true if key in self._data else false

    def keys(self) -> List:
        from poop.types.list import List

        return List(*self._data.keys())

    def values(self) -> List:
        from poop.types.list import List

        return List(*self._data.values())

    def do(self, block: Callable[[Tuple], Any]) -> None:
        from poop.types.tuple import Tuple

        deque((block(Tuple(k, v)) for k, v in self._data.items()), maxlen=0)

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._data))

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._data)

    def __contains__(self, item: object) -> bool:
        return item in self._data

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Dict):
            return true if self._data == other._data else false
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Dict):
            return false if self._data == other._data else true
        return true

    def __str__(self) -> str:
        pairs = ", ".join(f"{k}: {v}" for k, v in self._data.items())
        return "{" + pairs + "}"

    __repr__ = __str__
