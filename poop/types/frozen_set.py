from typing import TYPE_CHECKING, ClassVar

from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin
from poop.types._set_algebra import _elements, _SetAlgebraMixin, probed
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import to_boolean
from poop.types.frozen_set_iterator import FrozenSetIterator
from poop.types.int import Int
from poop.types.object import Object

if TYPE_CHECKING:
    from collections.abc import Iterable

    from poop.types.boolean import Boolean


class FrozenSet(_SetAlgebraMixin, _ValueEqMixin, _IterableMixin, Object):
    __slots__ = ("_data",)
    _eq_attr: ClassVar[str] = "_data"
    _eq_group: ClassVar[str] = "set"

    def __init__(self, *elements: Object) -> None:
        self._data: frozenset[Object] = frozenset(elements)

    def includes(self, obj: Object) -> Boolean:
        return to_boolean(probed(obj) in self._data)

    def len(self) -> Int:
        return Int(len(self._data))

    def copy(self) -> FrozenSet:
        # CPython returns the receiver itself — a frozenset is immutable, so
        # copying it is pointless and ``fs.copy() is fs`` is True.
        return self

    def union(self, *others: Object) -> FrozenSet:
        return FrozenSet(*self._data.union(*(_elements(o, "union") for o in others)))

    def intersection(self, *others: Object) -> FrozenSet:
        return FrozenSet(
            *self._data.intersection(*(_elements(o, "intersection") for o in others))
        )

    def difference(self, *others: Object) -> FrozenSet:
        return FrozenSet(
            *self._data.difference(*(_elements(o, "difference") for o in others))
        )

    def symmetric_difference(self, other: Object) -> FrozenSet:
        return FrozenSet(
            *self._data.symmetric_difference(_elements(other, "symmetric_difference"))
        )

    def isdisjoint(self, other: Object) -> Boolean:
        return to_boolean(self._data.isdisjoint(_elements(other, "isdisjoint")))

    def issubset(self, other: Object) -> Boolean:
        return to_boolean(self._data.issubset(_elements(other, "issubset")))

    def issuperset(self, other: Object) -> Boolean:
        return to_boolean(self._data.issuperset(_elements(other, "issuperset")))

    def _rewrap(self, raw: Iterable[Object]) -> FrozenSet:
        return FrozenSet(*raw)

    def iter(self) -> FrozenSetIterator:
        return FrozenSetIterator(self._data)

    def __hash__(self) -> int:
        return hash(self._data)

    def __str__(self) -> str:
        if not self._data:
            return "frozenset()"
        return "frozenset({" + ", ".join(repr(item) for item in self._data) + "})"

    __repr__ = __str__


cloak(FrozenSet, "frozenset")
