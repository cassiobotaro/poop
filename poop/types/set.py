from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._iterable_mixin import _IterableMixin
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.none import none
from poop.types.object import Object
from poop.types.set_iterator import SetIterator

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.none import NoneClass

_set = set  # alias to avoid shadowing by Set class name in annotations


class Set(_ValueEqMixin, _IterableMixin, Object):
    __slots__ = ("_data",)
    _eq_attr: ClassVar[str] = "_data"
    __hash__ = None

    def __init__(self, *elements: Object) -> None:
        self._data: _set[Object] = _set(elements)

    def add(self, obj: Object) -> NoneClass:
        self._data.add(obj)
        return none

    def remove(self, obj: Object) -> NoneClass:
        self._data.remove(obj)
        return none

    def discard(self, obj: Object) -> NoneClass:
        self._data.discard(obj)
        return none

    def clear(self) -> NoneClass:
        self._data.clear()
        return none

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

    def update(self, *others: Set) -> NoneClass:
        self._data.update(*[o._data for o in others])
        return none

    def intersection_update(self, *others: Set) -> NoneClass:
        self._data.intersection_update(*[o._data for o in others])
        return none

    def difference_update(self, *others: Set) -> NoneClass:
        self._data.difference_update(*[o._data for o in others])
        return none

    def symmetric_difference_update(self, other: Set) -> NoneClass:
        self._data.symmetric_difference_update(other._data)
        return none

    def isdisjoint(self, other: Set) -> Boolean:
        return true if self._data.isdisjoint(other._data) else false

    def issubset(self, other: Set) -> Boolean:
        return true if self._data.issubset(other._data) else false

    def issuperset(self, other: Set) -> Boolean:
        return true if self._data.issuperset(other._data) else false

    def includes(self, obj: Object) -> Boolean:
        return true if obj in self._data else false

    def len(self) -> Int:
        return Int(len(self._data))

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._data)

    def iter(self) -> SetIterator:
        return SetIterator(self._data)

    def __contains__(self, item: object) -> bool:
        return item in self._data

    def __and__(self, other: object) -> Any:
        if not isinstance(other, Set):
            return NotImplemented
        return Set(*self._data & other._data)

    def __or__(self, other: object) -> Any:
        if not isinstance(other, Set):
            return NotImplemented
        return Set(*self._data | other._data)

    def __sub__(self, other: object) -> Any:
        if not isinstance(other, Set):
            return NotImplemented
        return Set(*self._data - other._data)

    def __xor__(self, other: object) -> Any:
        if not isinstance(other, Set):
            return NotImplemented
        return Set(*self._data ^ other._data)

    def __str__(self) -> str:
        if not self._data:
            return "set()"
        return "{" + ", ".join(repr(item) for item in self._data) + "}"

    __repr__ = __str__


Set.__module__ = "builtins"
Set.__name__ = "set"
