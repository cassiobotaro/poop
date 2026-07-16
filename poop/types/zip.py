import builtins as _builtins
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.boolean import false, to_boolean, true
from poop.types.object import Object
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.boolean import Boolean, to_boolean
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
        self._strict: Boolean = to_boolean(_unwrap_bool(strict, False))
        self._iter: Iterator[Tuple] | None = None

    @staticmethod
    def _gen(sources: tuple[Any, ...], strict: bool) -> Iterator[Tuple]:
        for items in _builtins.zip(*sources, strict=strict):
            yield Tuple(*items)

    def _materialize(self) -> Iterator[Tuple]:
        if self._iter is None:
            self._iter = self._gen(self._sources, bool(self._strict))
            # The generator now owns the sources; drop our copy so a consumed
            # Zip stops pinning all of its source iterables.
            self._sources = ()
        return self._iter

    def __iter__(self) -> Iterator[Tuple]:
        return self._materialize()

    def iter(self) -> Zip:
        return self

    def next(self) -> Tuple:
        return next(self._materialize())

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(self is other)

    def __ne__(self, other: object) -> Boolean:

        return false if self is other else true

    def __str__(self) -> str:
        return "<zip>"

    __repr__ = __str__


Zip.__module__ = "builtins"
Zip.__name__ = "zip"
