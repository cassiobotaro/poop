from builtins import print as _builtins_print
from builtins import reversed as builtins_reversed
from builtins import sorted as builtins_sorted
from collections.abc import Callable, Iterable, Iterator
from typing import TYPE_CHECKING, Any, ClassVar, Self, cast

from poop.types._iterable_mixin import _IterableMixin
from poop.types._repeat import _repeat_count
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import false, to_boolean
from poop.types.list_iterator import ListIterator
from poop.types.none import none
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types._index import Index
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

    def at(self, index: Index | Slice) -> Object:
        from poop.types.slice import Slice

        if isinstance(index, Slice):
            return List(*self._items[index._py_slice()])
        return self._items[index]

    def slice(
        self,
        start_or_slice: Index | Slice,
        stop: Index | NoneClass | None = None,
        step: Index | NoneClass | None = None,
    ) -> List:
        from poop.types.slice import _resolve_py_slice

        py = _resolve_py_slice(start_or_slice, stop, step)
        return List(*self._items[py])

    def __add__(self, other: object) -> List:
        if not isinstance(other, List):
            return NotImplemented  # foreign operand -> faithful TypeError
        return List(*self._items + other._items)

    def __lt__(self, other: object) -> Boolean:
        if not isinstance(other, List):
            return NotImplemented  # foreign operand -> faithful TypeError
        a = cast("_list[Any]", self._items)
        b = cast("_list[Any]", other._items)
        return to_boolean(a < b)

    def __le__(self, other: object) -> Boolean:
        if not isinstance(other, List):
            return NotImplemented
        a = cast("_list[Any]", self._items)
        b = cast("_list[Any]", other._items)
        return to_boolean(a <= b)

    def __gt__(self, other: object) -> Boolean:
        if not isinstance(other, List):
            return NotImplemented
        a = cast("_list[Any]", self._items)
        b = cast("_list[Any]", other._items)
        return to_boolean(a > b)

    def __ge__(self, other: object) -> Boolean:
        if not isinstance(other, List):
            return NotImplemented
        a = cast("_list[Any]", self._items)
        b = cast("_list[Any]", other._items)
        return to_boolean(a >= b)

    def __mul__(self, other: object) -> List:
        return List(*self._items * _repeat_count(other))

    def __rmul__(self, other: object) -> List:
        return List(*self._items * _repeat_count(other))

    # In-place sequence operators mutate the receiver (CPython ``xs += ys`` is
    # ``list.extend`` and ``xs *= n`` repeats in place, so ``xs`` keeps its
    # identity and aliases observe the change). Without these, augmented
    # assignment would fall back to the binary ``__add__``/``__mul__``, rebind
    # the name to a fresh List, and silently leave any alias pointing at the
    # unchanged original. ``+=`` takes any iterable, like ``extend`` and unlike
    # ``__add__``, which stays List-only.
    def __iadd__(self, other: Iterable[Object]) -> Self:
        self._items.extend(other)
        return self

    def __imul__(self, other: object) -> Self:
        self._items *= _repeat_count(other)
        return self

    def __iter__(self) -> Iterator[Object]:
        return iter(self._items)

    def iter(self) -> ListIterator:
        return ListIterator(self._items)

    def includes(self, obj: Object) -> Boolean:
        return to_boolean(obj in self._items)

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def sorted(
        self,
        key: Callable[[Object], Any] | None = None,
        reverse: Boolean = false,
    ) -> List:
        return List(*builtins_sorted(self._items, key=key, reverse=bool(reverse)))

    def reversed(self) -> List:
        return List(*builtins_reversed(self._items))

    def append(self, obj: Object) -> NoneClass:
        self._items.append(obj)
        return none

    def pop(self, index: Index | NoneClass | None = None) -> Object:
        from poop.types._unwrap import _is_absent

        if _is_absent(index):
            return self._items.pop()
        return self._items.pop(index)

    def clear(self) -> NoneClass:
        self._items.clear()
        return none

    def copy(self) -> List:
        return List(*self._items)

    def count(self, obj: Object) -> Int:
        from poop.types.int import Int

        return Int(self._items.count(obj))

    def extend(self, other: Iterable[Object]) -> NoneClass:
        self._items.extend(other)
        return none

    def index(
        self,
        obj: Object,
        start: Int | NoneClass | None = None,
        stop: Index | NoneClass | None = None,
    ) -> Int:
        from poop.types._unwrap import _is_absent, _opt_int
        from poop.types.int import Int

        if _is_absent(start):
            return Int(self._items.index(obj))
        if _is_absent(stop):
            return Int(self._items.index(obj, _opt_int(start, 0)))
        return Int(self._items.index(obj, _opt_int(start, 0), _opt_int(stop, 0)))

    def insert(self, i: Index, obj: Object) -> NoneClass:
        self._items.insert(i, obj)
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
