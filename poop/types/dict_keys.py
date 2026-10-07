from typing import TYPE_CHECKING, Any, final

from poop.types._argument import a_collection
from poop.types._dict_view import _elements, _SetLikeView
from poop.types.boolean import to_boolean
from poop.types.dict_key_iterator import DictKeyIterator
from poop.types.dict_reverse_key_iterator import DictReverseKeyIterator

if TYPE_CHECKING:
    from collections.abc import Iterator

    from poop.types.boolean import Boolean
    from poop.types.object import Object


@final
class DictKeys(_SetLikeView, name="dict_keys"):
    """Live view over a Dict's keys, mirroring Python's dict_keys."""

    __slots__ = ()

    def _own(self) -> Any:
        return self._dict._data.keys()

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
        return to_boolean(
            self._own().isdisjoint(_elements(a_collection(other, "isdisjoint")))
        )

    def _repr_items(self) -> str:
        return ", ".join(repr(k) for k in self._dict._data)
