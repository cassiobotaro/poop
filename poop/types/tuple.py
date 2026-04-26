from builtins import reversed as builtins_reversed
from builtins import sorted as builtins_sorted
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.none import NoneClass

_tuple = tuple  # alias to avoid shadowing by Tuple class name in annotations


class Tuple(_IterableMixin, Object):
    __slots__ = ("_items",)

    def __init__(self, *elements: Object) -> None:
        self._items: _tuple[Object, ...] = _tuple(elements)

    def _collect(self, items: Any) -> Tuple:
        return Tuple(*items)

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._items))

    def __len__(self) -> int:
        return len(self._items)

    def at(self, index: Int) -> Object:
        return self._items[index._value]

    def copy_from_to(self, start: Int, stop: Int, step: Int | None = None) -> Tuple:
        s = step._value if step is not None else None
        return Tuple(*self._items[start._value : stop._value : s])

    def __add__(self, other: Tuple) -> Tuple:
        return Tuple(*self._items + other._items)

    def __mul__(self, other: Int) -> Tuple:
        return Tuple(*self._items * other._value)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._items)

    def includes(self, obj: Object) -> Boolean:
        from poop.types.boolean import false, true

        return true if obj in self._items else false

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def sorted(self, key: Callable[[Object], Any] | None = None) -> Tuple:
        return Tuple(*builtins_sorted(self._items, key=key))

    def reversed(self) -> Tuple:
        return Tuple(*builtins_reversed(self._items))

    def count(self, obj: Object) -> Int:
        from poop.types.int import Int

        return Int(self._items.count(obj))

    def index(self, obj: Object) -> Int:
        from poop.types.int import Int

        return Int(self._items.index(obj))

    def first(self) -> Object:
        return self._items[0]

    def last(self) -> Object:
        return self._items[-1]

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Tuple):
            return true if self._items == other._items else false
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Tuple):
            return false if self._items == other._items else true
        return true

    def __hash__(self) -> int:
        return hash(self._items)

    def print(self, sep: str = " ", end: str = "\n", flush: bool = False) -> Tuple:
        from builtins import print as _builtins_print

        _builtins_print(
            *[str(item) for item in self._items], sep=sep, end=end, flush=flush
        )  # noqa: T201
        return self

    def __str__(self) -> str:
        if len(self._items) == 1:
            return f"({self._items[0]},)"
        return f"({', '.join(str(item) for item in self._items)})"

    __repr__ = __str__
