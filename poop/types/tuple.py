import builtins
from reprlib import recursive_repr
from typing import TYPE_CHECKING, ClassVar

from poop.types._at import at_index
from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin, _sorted
from poop.types._ordered import _OrderedMixin
from poop.types._sequence import _SequenceMixin
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import false, to_boolean
from poop.types.int import Int
from poop.types.object import Object
from poop.types.slice import _resolve_py_slice
from poop.types.tuple_iterator import TupleIterator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from poop.types._argument import Key
    from poop.types._index import Index
    from poop.types.boolean import Boolean
    from poop.types.none import NoneClass
    from poop.types.slice import Slice
    from poop.types.string import Str


class Tuple(
    _SequenceMixin, _OrderedMixin, _ValueEqMixin, _IterableMixin[Object], Object
):
    __slots__ = ("_items",)
    _eq_attr: ClassVar[str] = "_items"

    def _rewrap(self, raw: Iterable[Object]) -> Tuple:
        return Tuple(*raw)

    def __init__(self, *elements: Object) -> None:
        self._items: tuple[Object, ...] = tuple(elements)

    def len(self) -> Int:
        return Int(len(self._items))

    def at(self, index: Index) -> Object:
        return at_index(self._items, index, self)

    def slice(
        self,
        start_or_slice: Index | Slice | NoneClass | None,
        stop: Index | NoneClass | None = None,
        step: Index | NoneClass | None = None,
    ) -> Tuple:
        py = _resolve_py_slice(start_or_slice, stop, step)
        return Tuple(*self._items[py])

    def __add__(self, other: object) -> Tuple:
        if not isinstance(other, Tuple):
            return NotImplemented  # foreign operand -> faithful TypeError
        return Tuple(*self._items + other._items)

    def iter(self) -> TupleIterator:
        return TupleIterator(self._items)

    def includes(self, obj: Object) -> Boolean:
        return to_boolean(obj in self)

    def sorted(
        self,
        *,
        key: Key[Object] = None,
        reverse: Boolean = false,
    ) -> Tuple:
        # Keyword-only, as on `List.sorted` — CPython's `sorted` takes only the
        # iterable positionally.
        return Tuple(*_sorted(self._items, key, reverse))

    def reversed(self) -> Tuple:
        return Tuple(*builtins.reversed(self._items))

    def count(self, obj: Object) -> Int:
        return Int(self._items.count(obj))

    def index(
        self,
        obj: Object,
        start: Int | NoneClass | None = None,
        stop: Index | NoneClass | None = None,
    ) -> Int:
        return self._index_of(obj, start, stop)

    def __hash__(self) -> int:
        return hash(self._items)

    def print(
        self,
        sep: Str | NoneClass | None = None,
        end: Str | NoneClass | None = None,
        flush: Boolean | NoneClass | None = None,
    ) -> NoneClass:
        return self._print_items(sep, end, flush)

    # A tuple is immutable but not acyclic — it can hold a list that holds the
    # tuple — so it needs the same cycle guard as `List`. See the note there.
    @recursive_repr(fillvalue="(...)")
    def __str__(self) -> str:
        if len(self._items) == 1:
            return f"({self._items[0]!r},)"
        return f"({', '.join(repr(item) for item in self._items)})"

    __repr__ = __str__


cloak(Tuple, "tuple")
