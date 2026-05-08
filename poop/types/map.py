from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class Map(_IterableMixin, Object):
    __slots__ = ("_iter", "_source", "_block")

    def __init__(self, source: Any, block: Callable[[Any], Any]) -> None:
        self._source = source
        self._block = block
        self._iter: Iterator[Any] | None = None

    def _gen(self) -> Iterator[Any]:
        for item in self._source:
            yield self._block(item)

    def __iter__(self) -> Iterator[Any]:
        return self._gen()

    def iter(self) -> Map:
        return self

    def next(self) -> Any:
        if self._iter is None:
            self._iter = self._gen()
        return next(self._iter)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return true if self is other else false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if self is other else true

    def __str__(self) -> str:
        return "<map>"

    __repr__ = __str__
