from itertools import starmap
from typing import TYPE_CHECKING, final

from poop.types._argument import a_collection
from poop.types._dict_view import _elements, _SetLikeView
from poop.types.boolean import to_boolean
from poop.types.dict_item_iterator import DictItemIterator
from poop.types.dict_reverse_item_iterator import DictReverseItemIterator
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from collections.abc import Iterator

    from poop.types.boolean import Boolean
    from poop.types.object import Object


@final
class DictItems(_SetLikeView[Tuple], name="dict_items"):
    """Live view over a Dict's items, mirroring Python's dict_items."""

    __slots__ = ()

    def __iter__(self) -> Iterator[Tuple]:
        return starmap(Tuple, self._dict._data.items())

    def iter(self) -> DictItemIterator:
        return DictItemIterator(self._dict._data.items())

    def reversed(self) -> DictReverseItemIterator:
        return DictReverseItemIterator(reversed(self._dict._data.items()))

    __reversed__ = reversed

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
        return to_boolean(
            self._own().isdisjoint(_elements(a_collection(other, "isdisjoint")))
        )

    def _own(self) -> set[Object]:
        # Mirroring CPython, an operand's members are *not* required to be
        # 2-tuples: `dict.items() ^ {99}` keeps the 99, so non-pair elements
        # must survive `|`/`^` rather than be dropped. Only the *own* side is
        # built from pairs.
        return set(starmap(Tuple, self._dict._data.items()))

    def _repr_items(self) -> str:
        return ", ".join(f"({k!r}, {v!r})" for k, v in self._dict._data.items())
