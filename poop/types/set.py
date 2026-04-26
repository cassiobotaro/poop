from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int

_set = set  # alias to avoid shadowing by Set class name in annotations


class Set(_IterableMixin, Object):
    __slots__ = ("_data",)
    __hash__ = None

    def __init__(self, *elements: Object) -> None:
        self._data: _set[Object] = _set(elements)

    def _collect(self, items: Any) -> Set:
        return Set(*items)

    def add(self, obj: Object) -> Set:
        self._data.add(obj)
        return self

    def remove(self, obj: Object) -> Set:
        self._data.remove(obj)
        return self

    def discard(self, obj: Object) -> Set:
        self._data.discard(obj)
        return self

    def clear(self) -> Set:
        self._data.clear()
        return self

    def copy(self) -> Set:
        return Set(*self._data)

    def pop(self) -> Object:
        return self._data.pop()

    def union(self, *others: Set) -> Set:
        return Set(*self._data.union(*[o._data for o in others]))

    def intersection(self, *others: Set) -> Set:
        return Set(*self._data.intersection(*[o._data for o in others]))

    def difference(self, *others: Set) -> Set:
        return Set(*self._data.difference(*[o._data for o in others]))

    def symmetric_difference(self, other: Set) -> Set:
        return Set(*self._data.symmetric_difference(other._data))

    def update(self, *others: Set) -> Set:
        self._data.update(*[o._data for o in others])
        return self

    def intersection_update(self, *others: Set) -> Set:
        self._data.intersection_update(*[o._data for o in others])
        return self

    def difference_update(self, *others: Set) -> Set:
        self._data.difference_update(*[o._data for o in others])
        return self

    def symmetric_difference_update(self, other: Set) -> Set:
        self._data.symmetric_difference_update(other._data)
        return self

    def isdisjoint(self, other: Set) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._data.isdisjoint(other._data) else false

    def issubset(self, other: Set) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._data.issubset(other._data) else false

    def issuperset(self, other: Set) -> Boolean:
        from poop.types.boolean import false, true

        return true if self._data.issuperset(other._data) else false

    def includes(self, obj: Object) -> Boolean:
        from poop.types.boolean import false, true

        return true if obj in self._data else false

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

        if isinstance(other, Set):
            return true if self._data == other._data else false
        return false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        if isinstance(other, Set):
            return false if self._data == other._data else true
        return true

    def __and__(self, other: Set) -> Set:
        return Set(*self._data & other._data)

    def __or__(self, other: Set) -> Set:
        return Set(*self._data | other._data)

    def __sub__(self, other: Set) -> Set:
        return Set(*self._data - other._data)

    def __xor__(self, other: Set) -> Set:
        return Set(*self._data ^ other._data)

    def __str__(self) -> str:
        if not self._data:
            return "set()"
        return "{" + ", ".join(repr(item) for item in self._data) + "}"

    __repr__ = __str__
