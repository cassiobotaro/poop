from __future__ import annotations

import builtins as _builtins
import itertools as _itertools
from abc import abstractmethod
from collections import deque
from collections.abc import Callable, Iterator
from functools import reduce as functools_reduce
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from poop.types.none import NoneClass

from poop.types.boolean import to_boolean
from poop.types.int import Int
from poop.types.none import none

_MISSING: Any = object()


class _IterableMixin:
    @abstractmethod
    def __iter__(self) -> Iterator[Any]: ...

    def _iter_items(self) -> Iterator[Any]:
        return iter(self)

    def do(self, block: Callable[[Any], Any]) -> NoneClass:
        deque(map(block, self._iter_items()), maxlen=0)
        return none

    def map(self, block: Callable[[Any], Any]) -> Any:
        from poop.types.map import Map

        return Map(self, block)

    def filter(self, block: Callable[[Any], Any]) -> Any:
        from poop.types.filter import Filter

        return Filter(self, block)

    def filter_false(self, block: Callable[[Any], Any]) -> Any:
        from poop.types.filter import Filter

        return Filter(self, lambda x: not bool(block(x)))

    def find(self, block: Callable[[Any], Any]) -> Any:
        for item in self._iter_items():
            if bool(block(item)):
                return item
        return none

    def reduce(self, init: Any, block: Callable[[Any, Any], Any]) -> Any:
        return functools_reduce(block, self._iter_items(), init)

    def sum(self) -> Any:
        items = list(self._iter_items())
        if not items:
            return Int(0)
        return functools_reduce(lambda a, b: a + b, items)

    def min(
        self,
        key: Callable[[Any], Any] | None = None,
        default: Any = _MISSING,
    ) -> Any:
        kwargs: dict[str, Any] = {}
        if key is not None:
            kwargs["key"] = key
        if default is not _MISSING:
            kwargs["default"] = default
        return _builtins.min(self._iter_items(), **kwargs)

    def max(
        self,
        key: Callable[[Any], Any] | None = None,
        default: Any = _MISSING,
    ) -> Any:
        kwargs: dict[str, Any] = {}
        if key is not None:
            kwargs["key"] = key
        if default is not _MISSING:
            kwargs["default"] = default
        return _builtins.max(self._iter_items(), **kwargs)

    def all(self, block: Callable[[Any], Any]) -> Any:
        return to_boolean(_builtins.all(bool(block(x)) for x in self._iter_items()))

    def any(self, block: Callable[[Any], Any]) -> Any:
        return to_boolean(_builtins.any(bool(block(x)) for x in self._iter_items()))

    def enumerate(self, start: Any = None) -> Any:
        from poop.types.enumerate import Enumerate

        return Enumerate(self, start)

    def zip(self, *others: Any, strict: Any = None) -> Any:
        from poop.types.zip import Zip

        return Zip(self, *others, strict=strict)

    def pairwise(self) -> Any:
        from poop.types.itertools import Pairwise
        from poop.types.tuple import Tuple

        return Pairwise(
            lambda: (Tuple(a, b) for a, b in _itertools.pairwise(self._iter_items()))
        )

    def batched(self, n: Any) -> Any:
        from poop.types.itertools import Batched
        from poop.types.tuple import Tuple

        return Batched(
            lambda: (
                Tuple(*batch)
                for batch in _itertools.batched(self._iter_items(), n._value)
            )
        )

    def chain(self, *others: Any) -> Any:
        from poop.types.itertools import Chain

        return Chain(lambda: _itertools.chain(self._iter_items(), *others))

    def accumulate(self, block: Callable[[Any, Any], Any] | None = None) -> Any:
        from poop.types._unwrap import _is_absent
        from poop.types.itertools import Accumulate

        func = None if _is_absent(block) else block
        return Accumulate(lambda: _itertools.accumulate(self._iter_items(), func))

    def product(self, *others: Any) -> Any:
        from poop.types.itertools import Product
        from poop.types.tuple import Tuple

        return Product(
            lambda: (
                Tuple(*combo)
                for combo in _itertools.product(self._iter_items(), *others)
            )
        )

    def combinations(self, n: Any) -> Any:
        from poop.types.itertools import Combinations
        from poop.types.tuple import Tuple

        return Combinations(
            lambda: (
                Tuple(*combo)
                for combo in _itertools.combinations(self._iter_items(), n._value)
            )
        )

    def permutations(self, n: Any = None) -> Any:
        from poop.types._unwrap import _opt_int
        from poop.types.itertools import Permutations
        from poop.types.tuple import Tuple

        return Permutations(
            lambda: (
                Tuple(*combo)
                for combo in _itertools.permutations(self._iter_items(), _opt_int(n))
            )
        )
