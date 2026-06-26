from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class Filter(_IterableMixin, Object):
    __slots__ = ("_iter", "_source", "_block")

    def __init__(self, source: Any, block: Callable[[Any], Any]) -> None:
        self._source = source
        self._block = block
        self._iter: Iterator[Any] | None = None

    @staticmethod
    def _gen(source: Any, block: Callable[[Any], Any]) -> Iterator[Any]:
        for item in source:
            if bool(block(item)):
                yield item

    def __iter__(self) -> Iterator[Any]:
        if self._iter is None:
            self._iter = self._gen(self._source, self._block)
        return self._iter

    def iter(self) -> Filter:
        return self

    def next(self) -> Any:
        if self._iter is None:
            self._iter = self._gen(self._source, self._block)
        return next(self._iter)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(self is other)

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if self is other else true

    def __str__(self) -> str:
        return "<filter>"

    __repr__ = __str__


Filter.__module__ = "builtins"
Filter.__name__ = "filter"
