"""Lazy combinator iterators returned by the `_IterableMixin` messages
(`pairwise`, `batched`, `chain`, `accumulate`, `product`,
`combinations`, `permutations`) — POOP's `itertools`, surfaced as
messages on iterables instead of free functions.

Each class wraps a deferred generator factory: nothing is consumed
until iteration starts, mirroring CPython's itertools objects.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class _CombinatorBase(_IterableMixin, Object):
    __slots__ = ("_make", "_iter")

    def __init__(self, make: Callable[[], Iterator[Any]]) -> None:
        self._make = make
        self._iter: Iterator[Any] | None = None

    def __iter__(self) -> Iterator[Any]:
        if self._iter is None:
            self._iter = self._make()
        return self._iter

    def iter(self) -> _CombinatorBase:
        return self

    def next(self) -> Any:
        return next(iter(self))

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(self is other)

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if self is other else true

    def __str__(self) -> str:
        return f"<{type(self).__name__}>"

    __repr__ = __str__


class Pairwise(_CombinatorBase):
    __slots__ = ()


class Batched(_CombinatorBase):
    __slots__ = ()


class Chain(_CombinatorBase):
    __slots__ = ()


class Accumulate(_CombinatorBase):
    __slots__ = ()


class Product(_CombinatorBase):
    __slots__ = ()


class Combinations(_CombinatorBase):
    __slots__ = ()


class Permutations(_CombinatorBase):
    __slots__ = ()


for _cls in (Pairwise, Batched, Chain, Accumulate, Product, Combinations, Permutations):
    _cls.__module__ = "itertools"
    _cls.__name__ = _cls.__name__.lower()
