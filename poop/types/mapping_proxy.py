from typing import TYPE_CHECKING, final

from poop.types._at import at_key
from poop.types._iterable_mixin import _IterableMixin
from poop.types.boolean import false, to_boolean
from poop.types.int import Int
from poop.types.none import none
from poop.types.object import Object

# circular: _mapping imports mapping_proxy
lazy from poop.types._mapping import _MappingMixin

# circular: dict imports mapping_proxy
lazy from poop.types.dict import Dict

if TYPE_CHECKING:
    from collections.abc import Iterator

    from poop.types.boolean import Boolean
    from poop.types.dict_items import DictItems
    from poop.types.dict_key_iterator import DictKeyIterator
    from poop.types.dict_keys import DictKeys
    from poop.types.dict_reverse_key_iterator import DictReverseKeyIterator
    from poop.types.dict_values import DictValues
    from poop.types.none import NoneClass


def _mapping_data(other: object) -> dict[Object, Object] | None:
    """The raw dict behind a mapping operand, or `None` when it is not one.

    A `MappingProxy` stands for the mapping it wraps; a `Dict` or `FrozenDict`
    is one. Six sites asked the two questions in a row — the two `__eq__`s,
    `Dict.__ior__`, `Dict.update`, `FrozenDict.__or__` and the proxy's own
    merge — and a seventh would have been the one to leave the proxy out.
    Without the `None` an `else` branch reached `other._data` on any operand,
    so `proxy | 5` answered `int does not understand #_data`, a POOP internal,
    where CPython answers `unsupported operand type(s)`.
    """
    if isinstance(other, MappingProxy):
        other = other._dict
    if isinstance(other, _MappingMixin):
        return other._data
    return None


@final
class MappingProxy(_IterableMixin[Object], Object, name="mappingproxy"):
    """Read-only view over a mapping. Mirrors types.MappingProxyType."""

    __slots__ = ("_dict",)
    __hash__ = None

    def __init__(self, dict_: _MappingMixin) -> None:
        self._dict = dict_

    def at(self, key: Object) -> Object:
        # Not `self._dict.at(key)`: the message must name the receiver the
        # user sent it to, not the Dict behind the proxy.
        return at_key(self._dict._data, key, self)

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
        return self._dict.iter()

    def reversed(self) -> DictReverseKeyIterator:
        return self._dict.reversed()

    __reversed__ = reversed

    def __contains__(self, item: object) -> bool:
        return item in self._dict

    def copy(self) -> _MappingMixin:
        # `copy` is the one read message the mixin leaves to each class: a
        # `Dict` copies, a `FrozenDict` answers itself, as in CPython.
        return self._dict.copy()

    def __eq__(self, other: object) -> Boolean:
        other_data = _mapping_data(other)
        if other_data is None:
            return false
        return to_boolean(self._dict._data == other_data)

    def __or__(self, other: object) -> Dict:
        other_data = _mapping_data(other)
        if other_data is None:
            return NotImplemented  # foreign operand -> faithful TypeError
        return Dict._wrapping(self._dict._data | other_data)

    def __ror__(self, other: object) -> Dict:
        other_data = _mapping_data(other)
        if other_data is None:
            return NotImplemented
        return Dict._wrapping(other_data | self._dict._data)

    def __str__(self) -> str:
        return f"mappingproxy({self._dict})"
