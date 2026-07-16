import builtins as _builtins
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types._unwrap import _unwrap
from poop.types.int import Int
from poop.types.object import Object
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.none import NoneClass


class Enumerate(_IterableMixin, Object):
    __slots__ = ("_iter", "_source", "_start")

    def __init__(self, source: Any, start: Int | NoneClass | None = None) -> None:
        iter(source)
        self._source = source
        self._start: Int = Int(_unwrap(start, 0))
        self._iter: Iterator[Tuple] | None = None

    @staticmethod
    def _gen(source: Any, start: int) -> Iterator[Tuple]:
        for i, item in _builtins.enumerate(source, start):
            yield Tuple(Int(i), item)

    def _materialize(self) -> Iterator[Tuple]:
        if self._iter is None:
            self._iter = self._gen(self._source, self._start._value)
            # The generator now owns the source; drop our copy so a consumed
            # Enumerate stops pinning its whole source.
            self._source = None
        return self._iter

    def __iter__(self) -> Iterator[Tuple]:
        return self._materialize()

    def iter(self) -> Enumerate:
        return self

    def next(self) -> Tuple:
        return next(self._materialize())

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(self is other)

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if self is other else true

    def __str__(self) -> str:
        return "<enumerate>"

    __repr__ = __str__


Enumerate.__module__ = "builtins"
Enumerate.__name__ = "enumerate"
