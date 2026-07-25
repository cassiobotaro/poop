from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, final

from poop.types._dict_view import _DictView, _elements, _set_like_elements
from poop.types.boolean import false, to_boolean, true
from poop.types.dict_item_iterator import DictItemIterator
from poop.types.dict_reverse_item_iterator import DictReverseItemIterator
from poop.types.object import Object
from poop.types.set import Set
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean


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

    def isdisjoint(self, other: object) -> Boolean:
        return to_boolean(self._poop_own_set().isdisjoint(_elements(other)))

    def _poop_own_set(self) -> set[Object]:
        # Mirroring CPython, an operand's members are *not* required to be
        # 2-tuples: `dict.items() ^ {99}` keeps the 99, so non-pair elements
        # must survive `|`/`^` rather than be dropped. Only the *own* side is
        # built from pairs.
        return {Tuple(k, v) for k, v in self._dict._data.items()}

    def __or__(self, other: object) -> Set:
        return Set(*(self._poop_own_set() | _elements(other)))

    def __ror__(self, other: object) -> Set:
        return Set(*(_elements(other) | self._poop_own_set()))

    def __and__(self, other: object) -> Set:
        return Set(*(self._poop_own_set() & _elements(other)))

    def __rand__(self, other: object) -> Set:
        return Set(*(_elements(other) & self._poop_own_set()))

    def __sub__(self, other: object) -> Set:
        return Set(*(self._poop_own_set() - _elements(other)))

    def __rsub__(self, other: object) -> Set:
        return Set(*(_elements(other) - self._poop_own_set()))

    def __xor__(self, other: object) -> Set:
        return Set(*(self._poop_own_set() ^ _elements(other)))

    def __rxor__(self, other: object) -> Set:
        return Set(*(_elements(other) ^ self._poop_own_set()))

    def __eq__(self, other: object) -> Boolean:
        # Equality answers false for a non-set-like operand rather than
        # raising, exactly as `dict.items() == [...]` does in CPython.
        raw = _set_like_elements(other)
        if raw is None:
            return false
        return to_boolean(self._poop_own_set() == raw)

    def __ne__(self, other: object) -> Boolean:
        return false if bool(self.__eq__(other)) else true

    def __le__(self, other: object) -> Boolean:
        raw = _set_like_elements(other)
        if raw is None:
            return NotImplemented  # foreign operand -> faithful TypeError
        return to_boolean(self._poop_own_set() <= raw)

    def __lt__(self, other: object) -> Boolean:
        raw = _set_like_elements(other)
        if raw is None:
            return NotImplemented  # foreign operand -> faithful TypeError
        return to_boolean(self._poop_own_set() < raw)

    def __ge__(self, other: object) -> Boolean:
        raw = _set_like_elements(other)
        if raw is None:
            return NotImplemented  # foreign operand -> faithful TypeError
        return to_boolean(self._poop_own_set() >= raw)

    def __gt__(self, other: object) -> Boolean:
        raw = _set_like_elements(other)
        if raw is None:
            return NotImplemented  # foreign operand -> faithful TypeError
        return to_boolean(self._poop_own_set() > raw)

    def _repr_items(self) -> str:
        return ", ".join(f"({k!r}, {v!r})" for k, v in self._dict._data.items())
