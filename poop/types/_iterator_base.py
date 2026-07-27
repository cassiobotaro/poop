from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any, ClassVar

from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin
from poop.types.object import Object

# Sentinel distinguishing "no default given" from an explicit default, so
# `it.next()` still raises StopIteration while `it.next(default)` swallows it —
# mirroring Python's two-arg `next(iterator, default)`.
_MISSING: Any = object()


class _IteratorBase[T](_IterableMixin, Object):
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
            # class_name() reads type(x).__name__ — answer the CPython name.
            cloak(cls, name)

    def __init__(self, iterable: Iterable[Any]) -> None:
        self._iter: Iterator[Any] = iter(iterable)

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        return next(self._iter)

    def next(self, default: Any = _MISSING) -> T:
        try:
            return next(self._iter)
        except StopIteration:
            if default is not _MISSING:
                return default
            raise

    def __str__(self) -> str:
        return f"<{self._repr_name}>"

    __repr__ = __str__
