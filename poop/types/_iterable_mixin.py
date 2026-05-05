from __future__ import annotations

import builtins as _builtins
from abc import abstractmethod
from collections import deque
from collections.abc import Callable, Iterator
from functools import reduce as functools_reduce
from typing import Any, Self

from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.none import none


class _IterableMixin:
    @abstractmethod
    def __iter__(self) -> Iterator[Any]: ...

    def _iter_items(self) -> Iterator[Any]:
        return iter(self)

    def _collect(self, items: Any) -> Any:
        from poop.types.list import List  # circular: list.py imports _IterableMixin

        return List(*items)

    def do(self, block: Callable[[Any], Any]) -> Self:
        deque(map(block, self._iter_items()), maxlen=0)
        return self

    def map(self, block: Callable[[Any], Any]) -> Any:
        return self._collect(map(block, self._iter_items()))

    def filter(self, block: Callable[[Any], Any]) -> Any:
        return self._collect(x for x in self._iter_items() if bool(block(x)))

    def filter_false(self, block: Callable[[Any], Any]) -> Any:
        return self._collect(x for x in self._iter_items() if not bool(block(x)))

    def find(self, block: Callable[[Any], Any]) -> Any:
        for item in self._iter_items():
            if bool(block(item)):
                return item
        return none

    def sum(self) -> Any:
        items = list(self._iter_items())
        if not items:
            return Int(0)
        return functools_reduce(lambda a, b: a + b, items)

    def all(self, block: Callable[[Any], Any]) -> Any:
        return (
            true if _builtins.all(bool(block(x)) for x in self._iter_items()) else false
        )

    def any(self, block: Callable[[Any], Any]) -> Any:
        return (
            true if _builtins.any(bool(block(x)) for x in self._iter_items()) else false
        )

    def enumerate(self, start: Any = None) -> Any:
        from poop.types.enumerate import Enumerate

        return Enumerate(self, start)

    def zip(self, *others: Any, strict: Any = None) -> Any:
        from poop.types.zip import Zip

        return Zip(self, *others, strict=strict)
