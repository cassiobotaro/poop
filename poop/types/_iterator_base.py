from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable, Iterator
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types.none import none
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.none import NoneClass


class _IteratorBase[T](Object):
    """Base for one-shot POOP iterators.

    Wraps a Python iterator. `next()` raises `StopIteration` on exhaustion —
    catch it via `Try(...).except_(StopIteration, handler).run()`.

    Generic over the element type `T`: each concrete iterator declares
    the POOP type it yields (`ListIterator(_IteratorBase[Object])`,
    `StrIterator(_IteratorBase[Str])`, etc.). The `name=` kwarg sets
    the Python-style repr name so a single `__str__` can serve every
    iterator type:

        class ListIterator(_IteratorBase[Object], name="list_iterator"):
            __slots__ = ()
    """

    __slots__ = ("_iter",)
    _repr_name: ClassVar[str] = "iterator"

    def __init_subclass__(cls, *, name: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if name is not None:
            cls._repr_name = name

    def __init__(self, iterable: Iterable[Any]) -> None:
        self._iter: Iterator[Any] = iter(iterable)

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        return next(self._iter)

    def next(self) -> T:
        return next(self._iter)

    def do(self, block: Callable[[T], Any]) -> NoneClass:
        deque(map(block, self._iter), maxlen=0)
        return none

    def __str__(self) -> str:
        return f"<{self._repr_name}>"

    __repr__ = __str__
