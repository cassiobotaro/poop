from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.none import NoneClass

_frozenset = frozenset  # alias to avoid shadowing by FrozenSet class name


class FrozenSet(_IterableMixin, Object):
    __slots__ = ("_data",)

    def __init__(self, *elements: Object) -> None:
        self._data: _frozenset[Object] = _frozenset(elements)

    def _collect(self, items: Any) -> FrozenSet:
        return FrozenSet(*items)

    def includes(self, obj: Object) -> Boolean:
        from poop.types.boolean import false, true

        return true if obj in self._data else false

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._data))

    def __len__(self) -> int:
        return len(self._data)

    def copy(self) -> FrozenSet:
        return FrozenSet(*self._data)

    def union(self, *others: FrozenSet) -> FrozenSet:
        return FrozenSet(*self._data.union(*[o._data for o in others]))

    def intersection(self, *others: FrozenSet) -> FrozenSet:
        return FrozenSet(*self._data.intersection(*[o._data for o in others]))

    def difference(self, *others: FrozenSet) -> FrozenSet:
        return FrozenSet(*self._data.difference(*[o._data for o in others]))

    def symmetric_difference(self, other: FrozenSet) -> FrozenSet:
        return FrozenSet(*self._data.symmetric_difference(other._data))

    def isdisjoint(self, other: FrozenSet) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._data.isdisjoint(other._data) else false

    def issubset(self, other: FrozenSet) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._data.issubset(other._data) else false

    def issuperset(self, other: FrozenSet) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._data.issuperset(other._data) else false

    def __iter__(self) -> Iterator[Object]:
        return iter(self._data)

    def __contains__(self, item: object) -> bool:
        return item in self._data

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, FrozenSet):
            return true if self._data == other._data else false
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, FrozenSet):
            return false if self._data == other._data else true
        return true

    def __and__(self, other: FrozenSet) -> FrozenSet:
        return FrozenSet(*self._data & other._data)

    def __or__(self, other: FrozenSet) -> FrozenSet:
        return FrozenSet(*self._data | other._data)

    def __sub__(self, other: FrozenSet) -> FrozenSet:
        return FrozenSet(*self._data - other._data)

    def __xor__(self, other: FrozenSet) -> FrozenSet:
        return FrozenSet(*self._data ^ other._data)

    def __hash__(self) -> int:
        return hash(self._data)

    def __str__(self) -> str:
        if not self._data:
            return "frozenset()"
        return "frozenset({" + ", ".join(repr(item) for item in self._data) + "})"

    __repr__ = __str__
