import builtins as _builtins
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.boolean import false
from poop.types.object import Object
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class Zip(_IterableMixin, Object):
    __slots__ = ("_sources", "_strict")

    def __init__(self, *sources: Any, strict: Boolean | None = None) -> None:
        self._sources = sources
        self._strict: Boolean = false if strict is None else strict

    def __iter__(self) -> Iterator[Tuple]:
        for items in _builtins.zip(*self._sources, strict=bool(self._strict)):
            yield Tuple(*items)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return true if self is other else false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if self is other else true

    def __str__(self) -> str:
        return "<zip object>"

    __repr__ = __str__
