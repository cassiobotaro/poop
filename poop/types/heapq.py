import heapq as _heapq
from collections.abc import Callable, Iterable, Iterator
from typing import Any, cast

from poop.types.boolean import Boolean
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none


class HeapMerge:
    """Lazy iterator returned by `heapq.merge(...)` — iterating yields
    sorted-merged elements without materializing the full result.
    """

    __slots__ = ("_gen",)

    def __init__(self, gen: Iterator[Any]) -> None:
        self._gen = gen

    def __iter__(self) -> Iterator[Any]:
        return self._gen

    def to_list(self) -> List:
        return List(*self._gen)


class Heapq:
    """Namespace mirroring Python's `heapq` module — a binary min-heap
    on a regular POOP `List`. Mutators operate in place on the list's
    underlying buffer; queries return new POOP `List`s.
    """

    @staticmethod
    def heappush(heap: List, item: Any) -> NoneClass:
        _heapq.heappush(cast(Any, heap._items), item)
        return none

    @staticmethod
    def heappop(heap: List) -> Any:
        return _heapq.heappop(cast(Any, heap._items))

    @staticmethod
    def heappushpop(heap: List, item: Any) -> Any:
        return _heapq.heappushpop(cast(Any, heap._items), item)

    @staticmethod
    def heapreplace(heap: List, item: Any) -> Any:
        return _heapq.heapreplace(cast(Any, heap._items), item)

    @staticmethod
    def heapify(heap: List, /) -> NoneClass:
        _heapq.heapify(cast(Any, heap._items))
        return none

    @staticmethod
    def nlargest(
        n: Int,
        iterable: Iterable[Any],
        key: Callable[[Any], Any] | None = None,
    ) -> List:
        if key is None:
            return List(*_heapq.nlargest(n._value, cast(Any, iterable)))
        return List(*_heapq.nlargest(n._value, cast(Any, iterable), key=key))

    @staticmethod
    def nsmallest(
        n: Int,
        iterable: Iterable[Any],
        key: Callable[[Any], Any] | None = None,
    ) -> List:
        if key is None:
            return List(*_heapq.nsmallest(n._value, cast(Any, iterable)))
        return List(*_heapq.nsmallest(n._value, cast(Any, iterable), key=key))

    @staticmethod
    def merge(
        *iterables: Iterable[Any],
        key: Callable[[Any], Any] | None = None,
        reverse: Boolean | None = None,
    ) -> HeapMerge:
        reverse_flag = False if reverse is None else bool(reverse)
        return HeapMerge(iter(_heapq.merge(*iterables, key=key, reverse=reverse_flag)))
