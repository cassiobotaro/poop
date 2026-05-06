from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable, Iterator
from typing import TYPE_CHECKING, Any

from poop.types.none import none
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.none import NoneClass


class _IteratorBase(Object):
    """Base for one-shot POOP iterators.

    Wraps a Python iterator. `next()` raises `StopIteration` on exhaustion —
    catch it via `Try(...).except_(StopIteration, handler).run()`.
    """

    __slots__ = ("_iter",)

    def __init__(self, iterable: Iterable[Any]) -> None:
        self._iter: Iterator[Any] = iter(iterable)

    def __iter__(self) -> Iterator[Any]:
        return self

    def __next__(self) -> Any:
        return next(self._iter)

    def next(self) -> Any:
        return next(self._iter)

    def do(self, block: Callable[[Any], Any]) -> NoneClass:
        deque(map(block, self._iter), maxlen=0)
        return none
