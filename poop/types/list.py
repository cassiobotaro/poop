from builtins import all as builtins_all
from builtins import any as builtins_any
from builtins import reversed as builtins_reversed
from builtins import sorted as builtins_sorted
from collections import deque
from collections.abc import Callable, Iterator
from functools import reduce
from typing import TYPE_CHECKING, Any

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.none import NoneClass

_list = list  # alias to avoid shadowing by List class name in annotations


class List(Object):
    __slots__ = ("_items",)

    def __init__(self, *elements: Object) -> None:
        self._items: _list[Object] = _list(elements)

    def add(self, obj: Object) -> List:
        self._items.append(obj)
        return self

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._items))

    def __len__(self) -> int:
        return len(self._items)

    def at(self, index: Int) -> Object:
        return self._items[index._value]

    def __getitem__(self, index: Int) -> Object:
        return self.at(index)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._items)

    def includes(self, obj: Object) -> Boolean:
        from poop.types.boolean import false, true

        return true if obj in self._items else false

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def do(self, block: Callable[[Object], Any]) -> None:
        deque(map(block, self._items), maxlen=0)

    def map(self, block: Callable[[Object], Any]) -> List:
        return List(*map(block, self._items))

    def filter(self, block: Callable[[Object], Any]) -> List:
        return List(*[x for x in self._items if bool(block(x))])

    def filter_false(self, block: Callable[[Object], Any]) -> List:
        return List(*[x for x in self._items if not bool(block(x))])

    def find(self, block: Callable[[Object], Any]) -> Object | NoneClass:
        from poop.types.none import none

        for item in self._items:
            if bool(block(item)):
                return item
        return none

    def reduce(self, init: Any, block: Callable[[Any, Object], Any]) -> Any:
        return reduce(block, self._items, init)

    def all(self, block: Callable[[Object], Any]) -> Boolean:
        from poop.types.boolean import false, true

        return true if builtins_all(bool(block(x)) for x in self._items) else false

    def any(self, block: Callable[[Object], Any]) -> Boolean:
        from poop.types.boolean import false, true

        return true if builtins_any(bool(block(x)) for x in self._items) else false

    def sorted(self, key: Callable[[Object], Any] | None = None) -> List:
        return List(*builtins_sorted(self._items, key=key))

    def reversed(self) -> List:
        return List(*builtins_reversed(self._items))

    def pop(self) -> Object:
        return self._items.pop()

    def first(self) -> Object:
        return self._items[0]

    def last(self) -> Object:
        return self._items[-1]

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, List):
            return true if self._items == other._items else false
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, List):
            return false if self._items == other._items else true
        return true

    def print(self, sep: str = " ", end: str = "\n", flush: bool = False) -> List:
        from builtins import print as _builtins_print

        _builtins_print(
            *[str(item) for item in self._items], sep=sep, end=end, flush=flush
        )  # noqa: T201
        return self

    def __str__(self) -> str:
        return f"[{', '.join(str(item) for item in self._items)}]"

    __repr__ = __str__
