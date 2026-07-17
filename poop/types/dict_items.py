from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, final

from poop.types._dict_view import _DictView
from poop.types.boolean import false, to_boolean, true
from poop.types.dict_item_iterator import DictItemIterator
from poop.types.dict_reverse_item_iterator import DictReverseItemIterator
from poop.types.frozen_set import FrozenSet
from poop.types.object import Object
from poop.types.set import Set
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean


def _other_items(other: DictItems | Set | FrozenSet) -> set[Object]:
    """Return the set-like operand's elements as raw POOP objects.

    For another ``DictItems`` the elements are the ``Tuple(k, v)`` pairs; for a
    ``Set``/``FrozenSet`` they are its members verbatim. Mirroring CPython, the
    members are *not* required to be 2-tuples: ``dict.items() ^ {99}`` keeps the
    ``99``, so non-pair elements must survive ``|``/``^`` rather than be dropped.
    """
    if isinstance(other, DictItems):
        return {Tuple(k, v) for k, v in other._dict._data.items()}
    return set(other._data)


@final
class DictItems(_DictView, name="dict_items"):
    """Live view over a Dict's items, mirroring Python's dict_items."""

    __slots__ = ()

    def __iter__(self) -> Iterator[Tuple]:
        return (Tuple(k, v) for k, v in self._dict._data.items())

    def iter(self) -> DictItemIterator:
        return DictItemIterator(self._dict._data.items())

    def __reversed__(self) -> DictReverseItemIterator:
        return DictReverseItemIterator(reversed(self._dict._data.items()))

    def reversed(self) -> DictReverseItemIterator:
        return DictReverseItemIterator(reversed(self._dict._data.items()))

    def includes(self, pair: Tuple) -> Boolean:
        # Delegate to __contains__ so a non-Tuple argument answers false the way
        # Python's `1 in d.items()` does, instead of reaching `pair._items` on a
        # non-Tuple and leaking the internal `_items` name through dispatch.
        return to_boolean(pair in self)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, Tuple) or len(item._items) != 2:
            return False
        k, v = item._items
        return k in self._dict._data and bool(self._dict._data[k] == v)

    def isdisjoint(self, other: DictItems | Set | FrozenSet) -> Boolean:
        return to_boolean(self._poop_own_set().isdisjoint(_other_items(other)))

    def _poop_own_set(self) -> set[Object]:
        return {Tuple(k, v) for k, v in self._dict._data.items()}

    def __or__(self, other: DictItems | Set | FrozenSet) -> Set:
        return Set(*(self._poop_own_set() | _other_items(other)))

    def __ror__(self, other: DictItems | Set | FrozenSet) -> Set:
        return Set(*(_other_items(other) | self._poop_own_set()))

    def __and__(self, other: DictItems | Set | FrozenSet) -> Set:
        return Set(*(self._poop_own_set() & _other_items(other)))

    def __rand__(self, other: DictItems | Set | FrozenSet) -> Set:
        return Set(*(_other_items(other) & self._poop_own_set()))

    def __sub__(self, other: DictItems | Set | FrozenSet) -> Set:
        return Set(*(self._poop_own_set() - _other_items(other)))

    def __rsub__(self, other: DictItems | Set | FrozenSet) -> Set:
        return Set(*(_other_items(other) - self._poop_own_set()))

    def __xor__(self, other: DictItems | Set | FrozenSet) -> Set:
        return Set(*(self._poop_own_set() ^ _other_items(other)))

    def __rxor__(self, other: DictItems | Set | FrozenSet) -> Set:
        return Set(*(_other_items(other) ^ self._poop_own_set()))

    def __eq__(self, other: object) -> Boolean:
        if isinstance(other, (DictItems, Set, FrozenSet)):
            return to_boolean(self._poop_own_set() == _other_items(other))
        return false

    def __ne__(self, other: object) -> Boolean:
        return false if bool(self.__eq__(other)) else true

    def __le__(self, other: DictItems | Set | FrozenSet) -> Boolean:
        return to_boolean(self._poop_own_set() <= _other_items(other))

    def __lt__(self, other: DictItems | Set | FrozenSet) -> Boolean:
        return to_boolean(self._poop_own_set() < _other_items(other))

    def __ge__(self, other: DictItems | Set | FrozenSet) -> Boolean:
        return to_boolean(self._poop_own_set() >= _other_items(other))

    def __gt__(self, other: DictItems | Set | FrozenSet) -> Boolean:
        return to_boolean(self._poop_own_set() > _other_items(other))

    def _repr_items(self) -> str:
        return ", ".join(f"({k!r}, {v!r})" for k, v in self._dict._data.items())
