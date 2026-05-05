from builtins import print as _builtins_print
from builtins import reversed as builtins_reversed
from builtins import sorted as builtins_sorted
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.boolean import false, true
from poop.types.none import none
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.none import NoneClass
    from poop.types.slice import Slice

_list = list  # alias to avoid shadowing by List class name in annotations


class List(_IterableMixin, Object):
    __slots__ = ("_items",)
    __hash__ = None

    def __init__(self, *elements: Object) -> None:
        self._items: _list[Object] = _list(elements)

    def _collect(self, items: Any) -> List:
        return List(*items)

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

    def slice(
        self,
        start_or_slice: Int | Slice,
        stop: Int | None = None,
        step: Int | None = None,
    ) -> List:
        from poop.types.slice import Slice

        if isinstance(start_or_slice, Slice):
            s = (
                start_or_slice._step._value
                if start_or_slice._step is not None
                else None
            )
            return List(
                *self._items[
                    start_or_slice._start._value : start_or_slice._stop._value : s
                ]
            )
        if stop is None:
            raise TypeError("stop is required when start is an Int")
        s = step._value if step is not None else None
        return List(*self._items[start_or_slice._value : stop._value : s])

    def __add__(self, other: List) -> List:
        return List(*self._items + other._items)

    def __mul__(self, other: Int) -> List:
        return List(*self._items * other._value)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._items)

    def includes(self, obj: Object) -> Boolean:
        return true if obj in self._items else false

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def sorted(self, key: Callable[[Object], Any] | None = None) -> List:
        return List(*builtins_sorted(self._items, key=key))

    def reversed(self) -> List:
        return List(*builtins_reversed(self._items))

    def pop(self) -> Object:
        return self._items.pop()

    def clear(self) -> NoneClass:
        self._items.clear()
        return none

    def copy(self) -> List:
        return List(*self._items)

    def count(self, obj: Object) -> Int:
        from poop.types.int import Int

        return Int(self._items.count(obj))

    def extend(self, other: List) -> NoneClass:
        self._items.extend(other._items)
        return none

    def index(self, obj: Object) -> Int:
        from poop.types.int import Int

        return Int(self._items.index(obj))

    def insert(self, i: Int, obj: Object) -> NoneClass:
        self._items.insert(i._value, obj)
        return none

    def remove(self, obj: Object) -> NoneClass:
        self._items.remove(obj)
        return none

    def reverse(self) -> NoneClass:
        self._items.reverse()
        return none

    def sort(
        self, key: Callable[[Object], Any] | None = None, reverse: bool = False
    ) -> NoneClass:
        self._items[:] = builtins_sorted(self._items, key=key, reverse=reverse)
        return none

    def first(self) -> Object:
        return self._items[0]

    def last(self) -> Object:
        return self._items[-1]

    def __eq__(self, other: object) -> Boolean:
        if isinstance(other, List):
            return true if self._items == other._items else false
        return false

    def __ne__(self, other: object) -> Boolean:
        if isinstance(other, List):
            return false if self._items == other._items else true
        return true

    def print(self, sep: str = " ", end: str = "\n", flush: bool = False) -> None:
        _builtins_print(
            *[str(item) for item in self._items], sep=sep, end=end, flush=flush
        )  # noqa: T201

    def __str__(self) -> str:
        return f"[{', '.join(repr(item) for item in self._items)}]"

    __repr__ = __str__
