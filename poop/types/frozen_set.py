from builtins import all as builtins_all
from builtins import any as builtins_any
from collections import deque
from collections.abc import Callable, Iterator
from functools import reduce
from typing import TYPE_CHECKING, Any

from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.int import Int
    from poop.types.none import NoneClass

_frozenset = frozenset  # alias to avoid shadowing by FrozenSet class name


class FrozenSet(Object):
    __slots__ = ("_data",)

    def __init__(self, *elements: Object) -> None:
        self._data: _frozenset[Object] = _frozenset(elements)

    def includes(self, obj: Object) -> Boolean:
        from poop.types.boolean import false, true

        return true if obj in self._data else false

    def len(self) -> Int:
        from poop.types.int import Int

        return Int(len(self._data))

    def __len__(self) -> int:
        return len(self._data)

    def do(self, block: Callable[[Object], Any]) -> None:
        deque(map(block, self._data), maxlen=0)

    def map(self, block: Callable[[Object], Any]) -> FrozenSet:
        return FrozenSet(*map(block, self._data))

    def filter(self, block: Callable[[Object], Any]) -> FrozenSet:
        return FrozenSet(*[x for x in self._data if bool(block(x))])

    def filter_false(self, block: Callable[[Object], Any]) -> FrozenSet:
        return FrozenSet(*[x for x in self._data if not bool(block(x))])

    def find(self, block: Callable[[Object], Any]) -> Object | NoneClass:
        from poop.types.none import none

        for item in self._data:
            if bool(block(item)):
                return item
        return none

    def reduce(self, init: Any, block: Callable[[Any, Object], Any]) -> Any:
        return reduce(block, self._data, init)

    def sum(self) -> Object:
        from poop.types.int import Int

        items = list(self._data)
        if not items:
            return Int(0)
        return reduce(lambda a, b: a + b, items)

    def all(self, block: Callable[[Object], Any]) -> Boolean:
        from poop.types.boolean import false, true

        return true if builtins_all(bool(block(x)) for x in self._data) else false

    def any(self, block: Callable[[Object], Any]) -> Boolean:
        from poop.types.boolean import false, true

        return true if builtins_any(bool(block(x)) for x in self._data) else false

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
        return "frozenset({" + ", ".join(str(item) for item in self._data) + "})"

    __repr__ = __str__
