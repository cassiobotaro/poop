from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, final

from poop.types._iterable_mixin import _IterableMixin
from poop.types.boolean import false, to_boolean, true
from poop.types.dict_key_iterator import DictKeyIterator
from poop.types.dict_reverse_key_iterator import DictReverseKeyIterator
from poop.types.int import Int
from poop.types.none import none
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
    from poop.types.dict import Dict
    from poop.types.dict_items import DictItems
    from poop.types.dict_keys import DictKeys
    from poop.types.dict_values import DictValues
    from poop.types.none import NoneClass


@final
class MappingProxy(_IterableMixin, Object):
    """Read-only view over a Dict. Mirrors types.MappingProxyType."""

    __slots__ = ("_dict",)
    __hash__ = None  # type: ignore[assignment]

    def __init__(self, dict_: Dict) -> None:
        self._dict = dict_

    def at(self, key: Object) -> Object:
        return self._dict.at(key)

    def get(
        self, key: Object, default: Object | NoneClass = none
    ) -> Object | NoneClass:
        return self._dict.get(key, default)

    def includes(self, key: Object) -> Boolean:
        return self._dict.includes(key)

    def keys(self) -> DictKeys:
        return self._dict.keys()

    def values(self) -> DictValues:
        return self._dict.values()

    def items(self) -> DictItems:
        return self._dict.items()

    def len(self) -> Int:
        return Int(len(self._dict))

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self) -> Iterator[Object]:
        return iter(self._dict)

    def iter(self) -> DictKeyIterator:
        return DictKeyIterator(self._dict._data)

    def __reversed__(self) -> DictReverseKeyIterator:
        return DictReverseKeyIterator(reversed(self._dict._data))

    def reversed(self) -> DictReverseKeyIterator:
        return DictReverseKeyIterator(reversed(self._dict._data))

    def __contains__(self, item: object) -> bool:
        return item in self._dict

    def copy(self) -> Dict:
        return self._dict.copy()

    def __eq__(self, other: object) -> Boolean:
        if isinstance(other, MappingProxy):
            return to_boolean(self._dict == other._dict)
        from poop.types.dict import Dict

        if isinstance(other, Dict):
            return to_boolean(self._dict == other)
        return false

    def __ne__(self, other: object) -> Boolean:
        eq = self.__eq__(other)
        return false if bool(eq) else true

    def __or__(self, other: Dict | MappingProxy) -> Dict:
        from poop.types.dict import Dict

        other_data = (
            other._dict._data if isinstance(other, MappingProxy) else other._data
        )
        merged = Dict()
        merged._data = {**self._dict._data, **other_data}
        return merged

    def __str__(self) -> str:
        return f"mappingproxy({self._dict})"

    __repr__ = __str__
