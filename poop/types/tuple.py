from builtins import print as _builtins_print
from builtins import reversed as builtins_reversed
from builtins import sorted as builtins_sorted
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any, ClassVar, cast

from poop.types._iterable_mixin import _IterableMixin
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import to_boolean
from poop.types.none import none
from poop.types.object import Object
from poop.types.tuple_iterator import TupleIterator

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.int import Int
    from poop.types.none import NoneClass
    from poop.types.slice import Slice
    from poop.types.string import Str

_tuple = tuple  # alias to avoid shadowing by Tuple class name in annotations


class Tuple(_ValueEqMixin, _IterableMixin, Object):
    __slots__ = ("_items",)
    _eq_attr: ClassVar[str] = "_items"

    def __init__(self, *elements: Object) -> None:
        self._items: _tuple[Object, ...] = _tuple(elements)

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
        stop: Int | NoneClass | None = None,
        step: Int | NoneClass | None = None,
    ) -> Tuple:
        from poop.types.slice import Slice

        if isinstance(start_or_slice, Slice):
            py = start_or_slice._py_slice()
        else:
            py = Slice(start_or_slice, stop, step)._py_slice()
        return Tuple(*self._items[py])

    def __add__(self, other: Tuple) -> Tuple:
        return Tuple(*self._items + other._items)

    def __mul__(self, other: Int) -> Tuple:
        return Tuple(*self._items * other._value)

    def __rmul__(self, other: Int) -> Tuple:
        return Tuple(*self._items * other._value)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._items)

    def iter(self) -> TupleIterator:
        return TupleIterator(self._items)

    def includes(self, obj: Object) -> Boolean:
        return to_boolean(obj in self._items)

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

    def __lt__(self, other: Tuple) -> Boolean:
        a = cast("tuple[Any, ...]", self._items)
        b = cast("tuple[Any, ...]", other._items)
        return to_boolean(a < b)

    def __le__(self, other: Tuple) -> Boolean:
        a = cast("tuple[Any, ...]", self._items)
        b = cast("tuple[Any, ...]", other._items)
        return to_boolean(a <= b)

    def __gt__(self, other: Tuple) -> Boolean:
        a = cast("tuple[Any, ...]", self._items)
        b = cast("tuple[Any, ...]", other._items)
        return to_boolean(a > b)

    def __ge__(self, other: Tuple) -> Boolean:
        a = cast("tuple[Any, ...]", self._items)
        b = cast("tuple[Any, ...]", other._items)
        return to_boolean(a >= b)

    def __hash__(self) -> int:
        return hash(self._items)

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
        if len(self._items) == 1:
            return f"({repr(self._items[0])},)"
        return f"({', '.join(repr(item) for item in self._items)})"

    __repr__ = __str__


Tuple.__module__ = "builtins"
Tuple.__name__ = "tuple"
