from __future__ import annotations

import builtins as _builtins
from abc import abstractmethod
from collections import deque
from collections.abc import Callable, Iterator
from functools import reduce as functools_reduce
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from poop.types.boolean import Boolean
    from poop.types.enumerate import Enumerate
    from poop.types.filter import Filter
    from poop.types.map import Map
    from poop.types.none import NoneClass
    from poop.types.object import Object
    from poop.types.zip import Zip

from poop.types.boolean import to_boolean
from poop.types.int import Int
from poop.types.none import none

_MISSING: Any = object()


def _minmax(
    func: Callable[..., Any],
    iterable: Any,
    key: Callable[[Any], Any] | None,
    default: Any,
) -> Any:
    """Assemble the optional `key`/`default` kwargs and call `min`/`max`.

    A single home for the `min`/`max` message body shared by the iterable
    mixin, Dict and Str — each passing only its own iterable, since Dict and
    Str deliberately do not inherit the mixin. Both callers import `_MISSING`
    from here, so the sentinel identity that drives the `default` branch is the
    same object across all three sites.
    """
    kwargs: dict[str, Any] = {}
    if key is not None:
        kwargs["key"] = key
    if default is not _MISSING:
        kwargs["default"] = default
    return func(iterable, **kwargs)


def _sorted(iterable: Any, key: Callable[[Any], Any] | None, reverse: Any) -> Any:
    """Assemble the optional `key` kwarg and call `sorted`.

    Shared by List (`sorted` and the in-place `sort`) and Tuple, which each
    answer their own type and so cannot inherit a single message. Passing
    `key=None` explicitly would work at runtime but matches no `sorted`
    overload, so the kwarg is omitted when there is no key.
    """
    kwargs: dict[str, Any] = {"reverse": bool(reverse)}
    if key is not None:
        kwargs["key"] = key
    return _builtins.sorted(iterable, **kwargs)


class _IterableMixin:
    @abstractmethod
    def __iter__(self) -> Iterator[Any]: ...

    def _iter_items(self) -> Iterator[Any]:
        return iter(self)

    def do(self, block: Callable[[Any], Any]) -> NoneClass:
        deque(map(block, self._iter_items()), maxlen=0)
        return none

    def map(self, block: Callable[[Any], Any]) -> Map:
        from poop.types.map import Map

        return Map(self, block)

    def filter(self, block: Callable[[Any], Any]) -> Filter:
        from poop.types.filter import Filter

        return Filter(self, block)

    def filter_false(self, block: Callable[[Any], Any]) -> Filter:
        from poop.types.filter import Filter

        return Filter(self, lambda x: not bool(block(x)))

    def find(self, block: Callable[[Any], Any]) -> Any:
        for item in self._iter_items():
            if bool(block(item)):
                return item
        return none

    def reduce(self, init: Any, block: Callable[[Any, Any], Any]) -> Any:
        return functools_reduce(block, self._iter_items(), init)

    def sum(self, start: Any = _MISSING) -> Any:
        items = self._iter_items()
        if start is not _MISSING:
            return functools_reduce(lambda a, b: a + b, items, start)
        try:
            first = next(items)
        except StopIteration:
            return Int(0)
        return functools_reduce(lambda a, b: a + b, items, first)

    def min(
        self,
        key: Callable[[Any], Any] | None = None,
        default: Any = _MISSING,
    ) -> Any:
        return _minmax(_builtins.min, self._iter_items(), key, default)

    def max(
        self,
        key: Callable[[Any], Any] | None = None,
        default: Any = _MISSING,
    ) -> Any:
        return _minmax(_builtins.max, self._iter_items(), key, default)

    def all(self, block: Callable[[Any], Any]) -> Boolean:
        return to_boolean(_builtins.all(bool(block(x)) for x in self._iter_items()))

    def any(self, block: Callable[[Any], Any]) -> Boolean:
        return to_boolean(_builtins.any(bool(block(x)) for x in self._iter_items()))

    def enumerate(self, start: Int | NoneClass | None = None) -> Enumerate:
        from poop.types.enumerate import Enumerate

        return Enumerate(self, start)

    def zip(self, *others: Object, strict: Boolean | NoneClass | None = None) -> Zip:
        from poop.types.zip import Zip

        return Zip(self, *others, strict=strict)
