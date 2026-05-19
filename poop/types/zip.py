import builtins as _builtins
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.boolean import false, true
from poop.types.object import Object
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.none import NoneClass


class Zip(_IterableMixin, Object):
    __slots__ = ("_iter", "_sources", "_strict")

    def __init__(
        self, *sources: Any, strict: Boolean | NoneClass | None = None
    ) -> None:
        from poop.types._unwrap import _unwrap_bool

        for source in sources:
            iter(source)
        self._sources = sources
        self._strict: Boolean = true if _unwrap_bool(strict, False) else false
        self._iter: Iterator[Tuple] | None = None

    def _gen(self) -> Iterator[Tuple]:
        for items in _builtins.zip(*self._sources, strict=bool(self._strict)):
            yield Tuple(*items)

    def __iter__(self) -> Iterator[Tuple]:
        return self._gen()

    def iter(self) -> Zip:
        return self

    def next(self) -> Tuple:
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
        return "<zip>"

    __repr__ = __str__


Zip.__module__ = "builtins"
Zip.__name__ = "zip"
