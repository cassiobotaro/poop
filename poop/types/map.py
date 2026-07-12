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

    @staticmethod
    def _gen(source: Any, block: Any) -> Iterator[Any]:
        for item in source:
            yield block(item)

    def _materialize(self) -> Iterator[Any]:
        if self._iter is None:
            self._iter = self._gen(self._source, self._block)
            # The generator now owns the source and block; drop our copies so
            # a consumed Map stops pinning its whole source and its closure.
            self._source = None
            self._block = None
        return self._iter

    def __iter__(self) -> Iterator[Any]:
        return self._materialize()

    def iter(self) -> Map:
        return self

    def next(self) -> Any:
        return next(self._materialize())

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(self is other)

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if self is other else true

    def __str__(self) -> str:
        return "<map>"

    __repr__ = __str__


Map.__module__ = "builtins"
Map.__name__ = "map"
