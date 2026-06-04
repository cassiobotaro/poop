from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, final

from poop.types._dict_view import _DictView
from poop.types.boolean import to_boolean
from poop.types.dict_reverse_value_iterator import DictReverseValueIterator
from poop.types.dict_value_iterator import DictValueIterator
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean


@final
class DictValues(_DictView, name="dict_values"):
    """Live view over a Dict's values, mirroring Python's dict_values."""

    __slots__ = ()

    def __iter__(self) -> Iterator[Object]:
        return iter(self._dict._data.values())

    def iter(self) -> DictValueIterator:
        return DictValueIterator(self._dict._data.values())

    def __reversed__(self) -> DictReverseValueIterator:
        return DictReverseValueIterator(reversed(self._dict._data.values()))

    def reversed(self) -> DictReverseValueIterator:
        return DictReverseValueIterator(reversed(self._dict._data.values()))

    def includes(self, value: Object) -> Boolean:
        return to_boolean(value in self._dict._data.values())

    def __contains__(self, item: object) -> bool:
        return item in self._dict._data.values()

    def _repr_items(self) -> str:
        return ", ".join(repr(v) for v in self._dict._data.values())
