from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, final

from poop.types._dict_view import _DictView
from poop.types.boolean import false, to_boolean, true
from poop.types.dict_key_iterator import DictKeyIterator
from poop.types.dict_reverse_key_iterator import DictReverseKeyIterator
from poop.types.frozen_set import FrozenSet
from poop.types.object import Object
from poop.types.set import Set

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean


def _other_keys(other: DictKeys | Set | FrozenSet) -> set[Object] | frozenset[Object]:
    """Extract the underlying Python set-like from another set-like POOP view."""
    if isinstance(other, DictKeys):
        return set(other._dict._data.keys())
    return other._data


@final
class DictKeys(_DictView, name="dict_keys"):
    """Live view over a Dict's keys, mirroring Python's dict_keys."""

    __slots__ = ()

    def __iter__(self) -> Iterator[Object]:
        return iter(self._dict._data)

    def iter(self) -> DictKeyIterator:
        return DictKeyIterator(self._dict._data)

    def __reversed__(self) -> DictReverseKeyIterator:
        return DictReverseKeyIterator(reversed(self._dict._data))

    def reversed(self) -> DictReverseKeyIterator:
        return DictReverseKeyIterator(reversed(self._dict._data))

    def includes(self, key: Object) -> Boolean:
        return to_boolean(key in self._dict._data)

    def __contains__(self, item: object) -> bool:
        return item in self._dict._data

    def isdisjoint(self, other: DictKeys | Set | FrozenSet) -> Boolean:
        return to_boolean(self._dict._data.keys().isdisjoint(_other_keys(other)))

    def __or__(self, other: DictKeys | Set | FrozenSet) -> Set:
        return Set(*(self._dict._data.keys() | _other_keys(other)))

    def __ror__(self, other: DictKeys | Set | FrozenSet) -> Set:
        return Set(*(_other_keys(other) | self._dict._data.keys()))

    def __and__(self, other: DictKeys | Set | FrozenSet) -> Set:
        return Set(*(self._dict._data.keys() & _other_keys(other)))

    def __rand__(self, other: DictKeys | Set | FrozenSet) -> Set:
        return Set(*(_other_keys(other) & self._dict._data.keys()))

    def __sub__(self, other: DictKeys | Set | FrozenSet) -> Set:
        return Set(*(self._dict._data.keys() - _other_keys(other)))

    def __rsub__(self, other: DictKeys | Set | FrozenSet) -> Set:
        return Set(*(_other_keys(other) - self._dict._data.keys()))

    def __xor__(self, other: DictKeys | Set | FrozenSet) -> Set:
        return Set(*(self._dict._data.keys() ^ _other_keys(other)))

    def __rxor__(self, other: DictKeys | Set | FrozenSet) -> Set:
        return Set(*(_other_keys(other) ^ self._dict._data.keys()))

    def __eq__(self, other: object) -> Boolean:
        if isinstance(other, (DictKeys, Set, FrozenSet)):
            return (
                true
                if set(self._dict._data.keys()) == set(_other_keys(other))
                else false
            )
        return false

    def __ne__(self, other: object) -> Boolean:
        return false if bool(self.__eq__(other)) else true

    def __le__(self, other: DictKeys | Set | FrozenSet) -> Boolean:
        return to_boolean(self._dict._data.keys() <= set(_other_keys(other)))

    def __lt__(self, other: DictKeys | Set | FrozenSet) -> Boolean:
        return to_boolean(self._dict._data.keys() < set(_other_keys(other)))

    def __ge__(self, other: DictKeys | Set | FrozenSet) -> Boolean:
        return to_boolean(self._dict._data.keys() >= set(_other_keys(other)))

    def __gt__(self, other: DictKeys | Set | FrozenSet) -> Boolean:
        return to_boolean(self._dict._data.keys() > set(_other_keys(other)))

    def _repr_items(self) -> str:
        return ", ".join(repr(k) for k in self._dict._data)
