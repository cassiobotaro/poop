from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, final

from poop.types._dict_view import _DictView, _elements, _set_like_elements
from poop.types.boolean import false, to_boolean, true
from poop.types.dict_key_iterator import DictKeyIterator
from poop.types.dict_reverse_key_iterator import DictReverseKeyIterator
from poop.types.object import Object
from poop.types.set import Set

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean


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

    def isdisjoint(self, other: object) -> Boolean:
        return to_boolean(self._dict._data.keys().isdisjoint(_elements(other)))

    def __or__(self, other: object) -> Set:
        return Set(*(self._dict._data.keys() | _elements(other)))

    def __ror__(self, other: object) -> Set:
        return Set(*(_elements(other) | self._dict._data.keys()))

    def __and__(self, other: object) -> Set:
        return Set(*(self._dict._data.keys() & _elements(other)))

    def __rand__(self, other: object) -> Set:
        return Set(*(_elements(other) & self._dict._data.keys()))

    def __sub__(self, other: object) -> Set:
        return Set(*(self._dict._data.keys() - _elements(other)))

    def __rsub__(self, other: object) -> Set:
        return Set(*(_elements(other) - self._dict._data.keys()))

    def __xor__(self, other: object) -> Set:
        return Set(*(self._dict._data.keys() ^ _elements(other)))

    def __rxor__(self, other: object) -> Set:
        return Set(*(_elements(other) ^ self._dict._data.keys()))

    def __eq__(self, other: object) -> Boolean:
        # Equality answers false for a non-set-like operand rather than
        # raising, exactly as `dict.keys() == [...]` does in CPython.
        raw = _set_like_elements(other)
        if raw is None:
            return false
        return true if set(self._dict._data.keys()) == raw else false

    def __ne__(self, other: object) -> Boolean:
        return false if bool(self.__eq__(other)) else true

    def __le__(self, other: object) -> Boolean:
        raw = _set_like_elements(other)
        if raw is None:
            return NotImplemented  # foreign operand -> faithful TypeError
        return to_boolean(self._dict._data.keys() <= raw)

    def __lt__(self, other: object) -> Boolean:
        raw = _set_like_elements(other)
        if raw is None:
            return NotImplemented  # foreign operand -> faithful TypeError
        return to_boolean(self._dict._data.keys() < raw)

    def __ge__(self, other: object) -> Boolean:
        raw = _set_like_elements(other)
        if raw is None:
            return NotImplemented  # foreign operand -> faithful TypeError
        return to_boolean(self._dict._data.keys() >= raw)

    def __gt__(self, other: object) -> Boolean:
        raw = _set_like_elements(other)
        if raw is None:
            return NotImplemented  # foreign operand -> faithful TypeError
        return to_boolean(self._dict._data.keys() > raw)

    def _repr_items(self) -> str:
        return ", ".join(repr(k) for k in self._dict._data)
