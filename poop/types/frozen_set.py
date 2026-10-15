from typing import TYPE_CHECKING, ClassVar

from poop.types._iterable_mixin import _IterableMixin
from poop.types._set_algebra import _SetAlgebraMixin
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import to_boolean
from poop.types.frozen_set_iterator import FrozenSetIterator
from poop.types.int import Int
from poop.types.object import Object

if TYPE_CHECKING:
    from collections.abc import Iterable

    from poop.types.boolean import Boolean


class FrozenSet(
    _SetAlgebraMixin, _ValueEqMixin, _IterableMixin[Object], Object, name="frozenset"
):
    __slots__ = ("_data",)
    _data: frozenset[Object]
    _eq_attr: ClassVar[str] = "_data"
    _eq_group: ClassVar[str | None] = "set"

    def __init__(self, *elements: Object) -> None:
        self._data: frozenset[Object] = frozenset(elements)

    def includes(self, obj: Object) -> Boolean:
        return to_boolean(obj in self)

    def len(self) -> Int:
        return Int(len(self._data))

    def copy(self) -> FrozenSet:
        # CPython returns the receiver itself — a frozenset is immutable, so
        # copying it is pointless and ``fs.copy() is fs`` is True.
        return self

    def union(self, *others: Object) -> FrozenSet:
        return self._combined("union", others)

    def intersection(self, *others: Object) -> FrozenSet:
        return self._combined("intersection", others)

    def difference(self, *others: Object) -> FrozenSet:
        return self._combined("difference", others)

    def symmetric_difference(self, other: Object) -> FrozenSet:
        return self._combined("symmetric_difference", (other,))

    def isdisjoint(self, other: Object) -> Boolean:
        return self._asks("isdisjoint", other)

    def issubset(self, other: Object) -> Boolean:
        return self._asks("issubset", other)

    def issuperset(self, other: Object) -> Boolean:
        return self._asks("issuperset", other)

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
