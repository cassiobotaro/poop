from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, final

from poop.types._iterable_mixin import _IterableMixin
from poop.types.boolean import false, true
from poop.types.dict_item_iterator import DictItemIterator
from poop.types.dict_reverse_item_iterator import DictReverseItemIterator
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.mapping_proxy import MappingProxy
from poop.types.object import Object
from poop.types.set import Set
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.dict import Dict


def _other_items(other: Any) -> Any:
    """Extract the underlying Python iterable of (k, v) pairs."""
    if isinstance(other, DictItems):
        return other._dict._data.items()
    if isinstance(other, (Set, FrozenSet)):
        return {
            (t._items[0], t._items[1])
            for t in other._data
            if isinstance(t, Tuple) and len(t._items) == 2
        }
    if isinstance(other, set):
        return other
    return other


@final
class DictItems(_IterableMixin, Object):
    """Live view over a Dict's items, mirroring Python's dict_items."""

    __slots__ = ("_dict",)
    __hash__ = None  # type: ignore[assignment]

    def __init__(self, dict_: Dict) -> None:
        self._dict = dict_

    def len(self) -> Int:
        return Int(len(self._dict))

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self) -> Iterator[Tuple]:
        return (Tuple(k, v) for k, v in self._dict._data.items())

    def iter(self) -> DictItemIterator:
        return DictItemIterator(self._dict._data.items())

    def __reversed__(self) -> DictReverseItemIterator:
        return DictReverseItemIterator(reversed(self._dict._data.items()))

    def reversed(self) -> DictReverseItemIterator:
        return DictReverseItemIterator(reversed(self._dict._data.items()))

    def includes(self, pair: Tuple) -> Boolean:
        if len(pair._items) != 2:
            return false
        k, v = pair._items
        return true if k in self._dict._data and self._dict._data[k] == v else false

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, Tuple) or len(item._items) != 2:
            return False
        k, v = item._items
        return k in self._dict._data and bool(self._dict._data[k] == v)

    def isdisjoint(self, other: Any) -> Boolean:
        own = set(self._dict._data.items())
        return true if own.isdisjoint(_other_items(other)) else false

    def mapping(self) -> MappingProxy:
        return MappingProxy(self._dict)

    def _poop_own_set(self) -> set:
        return set(self._dict._data.items())

    def __or__(self, other: Any) -> Set:
        merged = self._poop_own_set() | set(_other_items(other))
        return Set(*(Tuple(k, v) for k, v in merged))

    def __ror__(self, other: Any) -> Set:
        merged = set(_other_items(other)) | self._poop_own_set()
        return Set(*(Tuple(k, v) for k, v in merged))

    def __and__(self, other: Any) -> Set:
        result = self._poop_own_set() & set(_other_items(other))
        return Set(*(Tuple(k, v) for k, v in result))

    def __rand__(self, other: Any) -> Set:
        result = set(_other_items(other)) & self._poop_own_set()
        return Set(*(Tuple(k, v) for k, v in result))

    def __sub__(self, other: Any) -> Set:
        result = self._poop_own_set() - set(_other_items(other))
        return Set(*(Tuple(k, v) for k, v in result))

    def __rsub__(self, other: Any) -> Set:
        result = set(_other_items(other)) - self._poop_own_set()
        return Set(*(Tuple(k, v) for k, v in result))

    def __xor__(self, other: Any) -> Set:
        result = self._poop_own_set() ^ set(_other_items(other))
        return Set(*(Tuple(k, v) for k, v in result))

    def __rxor__(self, other: Any) -> Set:
        result = set(_other_items(other)) ^ self._poop_own_set()
        return Set(*(Tuple(k, v) for k, v in result))

    def __eq__(self, other: object) -> Boolean:
        if isinstance(other, (DictItems, Set, FrozenSet)):
            return true if self._poop_own_set() == set(_other_items(other)) else false
        return false

    def __ne__(self, other: object) -> Boolean:
        return false if bool(self.__eq__(other)) else true

    def __le__(self, other: Any) -> Boolean:
        return true if self._poop_own_set() <= set(_other_items(other)) else false

    def __lt__(self, other: Any) -> Boolean:
        return true if self._poop_own_set() < set(_other_items(other)) else false

    def __ge__(self, other: Any) -> Boolean:
        return true if self._poop_own_set() >= set(_other_items(other)) else false

    def __gt__(self, other: Any) -> Boolean:
        return true if self._poop_own_set() > set(_other_items(other)) else false

    def __str__(self) -> str:
        items = ", ".join(f"({k!r}, {v!r})" for k, v in self._dict._data.items())
        return f"dict_items([{items}])"

    __repr__ = __str__
