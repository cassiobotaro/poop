from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, final

from poop.types._iterable_mixin import _IterableMixin
from poop.types.boolean import false, true
from poop.types.dict_key_iterator import DictKeyIterator
from poop.types.dict_reverse_key_iterator import DictReverseKeyIterator
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.mapping_proxy import MappingProxy
from poop.types.object import Object
from poop.types.set import Set

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.dict import Dict

_KeySetLike = "DictKeys | Set | FrozenSet"


def _other_keys(other: DictKeys | Set | FrozenSet) -> set[Object] | frozenset[Object]:
    """Extract the underlying Python set-like from another set-like POOP view."""
    if isinstance(other, DictKeys):
        return set(other._dict._data.keys())
    return other._data


@final
class DictKeys(_IterableMixin, Object):
    """Live view over a Dict's keys, mirroring Python's dict_keys."""

    __slots__ = ("_dict",)
    __hash__ = None  # type: ignore[assignment]

    def __init__(self, dict_: Dict) -> None:
        self._dict = dict_

    def len(self) -> Int:
        return Int(len(self._dict))

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._dict._data)

    def iter(self) -> DictKeyIterator:
        return DictKeyIterator(self._dict._data)

    def __reversed__(self) -> DictReverseKeyIterator:
        return DictReverseKeyIterator(reversed(self._dict._data))

    def reversed(self) -> DictReverseKeyIterator:
        return DictReverseKeyIterator(reversed(self._dict._data))

    def includes(self, key: Object) -> Boolean:
        return true if key in self._dict._data else false

    def __contains__(self, item: object) -> bool:
        return item in self._dict._data

    def isdisjoint(self, other: DictKeys | Set | FrozenSet) -> Boolean:
        return true if self._dict._data.keys().isdisjoint(_other_keys(other)) else false

    def mapping(self) -> MappingProxy:
        return MappingProxy(self._dict)

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
        return true if self._dict._data.keys() <= set(_other_keys(other)) else false

    def __lt__(self, other: DictKeys | Set | FrozenSet) -> Boolean:
        return true if self._dict._data.keys() < set(_other_keys(other)) else false

    def __ge__(self, other: DictKeys | Set | FrozenSet) -> Boolean:
        return true if self._dict._data.keys() >= set(_other_keys(other)) else false

    def __gt__(self, other: DictKeys | Set | FrozenSet) -> Boolean:
        return true if self._dict._data.keys() > set(_other_keys(other)) else false

    def __str__(self) -> str:
        items = ", ".join(repr(k) for k in self._dict._data)
        return f"dict_keys([{items}])"

    __repr__ = __str__
