from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, final

from poop.types._iterable_mixin import _IterableMixin
from poop.types.boolean import false, true
from poop.types.dict_reverse_value_iterator import DictReverseValueIterator
from poop.types.dict_value_iterator import DictValueIterator
from poop.types.int import Int
from poop.types.mapping_proxy import MappingProxy
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.dict import Dict


@final
class DictValues(_IterableMixin, Object):
    """Live view over a Dict's values, mirroring Python's dict_values."""

    __slots__ = ("_dict",)
    __hash__ = None  # type: ignore[assignment]

    def __init__(self, dict_: Dict) -> None:
        self._dict = dict_

    def len(self) -> Int:
        return Int(len(self._dict))

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._dict._data.values())

    def iter(self) -> DictValueIterator:
        return DictValueIterator(self._dict._data.values())

    def __reversed__(self) -> DictReverseValueIterator:
        return DictReverseValueIterator(reversed(self._dict._data.values()))

    def reversed(self) -> DictReverseValueIterator:
        return DictReverseValueIterator(reversed(self._dict._data.values()))

    def includes(self, value: Object) -> Boolean:
        return true if value in self._dict._data.values() else false

    def __contains__(self, item: object) -> bool:
        return item in self._dict._data.values()

    def mapping(self) -> MappingProxy:
        return MappingProxy(self._dict)

    def __str__(self) -> str:
        items = ", ".join(repr(v) for v in self._dict._data.values())
        return f"dict_values([{items}])"

    __repr__ = __str__
