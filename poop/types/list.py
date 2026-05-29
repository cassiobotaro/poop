from builtins import print as _builtins_print
from builtins import reversed as builtins_reversed
from builtins import sorted as builtins_sorted
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._iterable_mixin import _IterableMixin
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import false, to_boolean
from poop.types.list_iterator import ListIterator
from poop.types.none import none
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.int import Int
    from poop.types.none import NoneClass
    from poop.types.slice import Slice
    from poop.types.string import Str

_list = list  # alias to avoid shadowing by List class name in annotations


class List(_ValueEqMixin, _IterableMixin, Object):
    __slots__ = ("_items",)
    _eq_attr: ClassVar[str] = "_items"
    __hash__ = None

    def __init__(self, *elements: Object) -> None:
        self._items: _list[Object] = _list(elements)

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
            return List(*self._items[start_or_slice._py_slice()])
        if stop is None:
            raise TypeError("stop is required when start is an Int")
        s = step._value if step is not None else None
        return List(*self._items[start_or_slice._value : stop._value : s])

    def __add__(self, other: List) -> List:
        return List(*self._items + other._items)

    def __mul__(self, other: Int) -> List:
        return List(*self._items * other._value)

    def __rmul__(self, other: Int) -> List:
        return List(*self._items * other._value)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._items)

    def iter(self) -> ListIterator:
        return ListIterator(self._items)

    def includes(self, obj: Object) -> Boolean:
        return to_boolean(obj in self._items)

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def sorted(self, key: Callable[[Object], Any] | None = None) -> List:
        return List(*builtins_sorted(self._items, key=key))

    def reversed(self) -> List:
        return List(*builtins_reversed(self._items))

    def append(self, obj: Object) -> NoneClass:
        self._items.append(obj)
        return none

    def pop(self, index: Int | NoneClass | None = None) -> Object:
        from poop.types._unwrap import _is_absent

        if _is_absent(index):
            return self._items.pop()
        return self._items.pop(index._value)  # ty: ignore[unresolved-attribute]

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
        self,
        key: Callable[[Object], Any] | None = None,
        reverse: Boolean = false,
    ) -> NoneClass:
        self._items[:] = builtins_sorted(self._items, key=key, reverse=bool(reverse))
        return none

    def print(
        self,
        sep: Str | NoneClass | None = None,
        end: Str | NoneClass | None = None,
        flush: Boolean | NoneClass | None = None,
    ) -> NoneClass:
        from poop.types._unwrap import _unwrap, _unwrap_bool

        sep_value = _unwrap(sep, " ")
        end_value = _unwrap(end, "\n")
        flush_value = _unwrap_bool(flush, False)
        _builtins_print(
            *[str(item) for item in self._items],
            sep=sep_value,
            end=end_value,
            flush=flush_value,
        )  # noqa: T201
        return none

    def __str__(self) -> str:
        return f"[{', '.join(repr(item) for item in self._items)}]"

    __repr__ = __str__


List.__module__ = "builtins"
List.__name__ = "list"
