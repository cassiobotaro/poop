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

    def _gen(self) -> Iterator[Tuple]:
        for i, item in _builtins.enumerate(self._source, self._start._value):
            yield Tuple(Int(i), item)

    def __iter__(self) -> Iterator[Tuple]:
        return self._gen()

    def iter(self) -> Enumerate:
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
        return "<enumerate>"

    __repr__ = __str__


Enumerate.__module__ = "builtins"
Enumerate.__name__ = "enumerate"
