from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from poop.types._cloak import cloak
from poop.types._iterable_mixin import _IterableMixin
from poop.types._peek import _UNPEEKED, _PeekMixin
from poop.types.exceptions import MIRRORS
from poop.types.object import Object

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class Map(_PeekMixin, _IterableMixin, Object):
    __slots__ = ("_iter", "_source", "_block")

    def __init__(self, source: Any, block: Callable[[Any], Any]) -> None:
        self._source = source
        self._block = block
        self._iter: Iterator[Any] | None = None
        self._peeked: Any = _UNPEEKED

    @staticmethod
    def _gen(source: Any, block: Any) -> Iterator[Any]:
        for item in source:
            # Caught before it can leave the generator. PEP 479 would
            # otherwise rewrite it into `RuntimeError: generator raised
            # StopIteration` — a report about a construct POOP does not have
            # and `no_yield` bans, read by someone who never wrote one. What
            # PEP 479 is *protecting* against stays protected: letting the
            # StopIteration through would end the view early and answer a
            # quietly truncated collection.
            try:
                value = block(item)
            except StopIteration:
                raise MIRRORS["RuntimeError"](
                    "a block ran off the end of an iterator — "
                    "ask #has_next before #next"
                ) from None
            yield value

    def _materialize(self) -> Iterator[Any]:
        if self._iter is None:
            self._iter = self._gen(self._source, self._block)
            # The generator now owns the source and block; drop our copies so
            # a consumed Map stops pinning its whole source and its closure.
            self._source = None
            self._block = None
        return self._iter

    def __iter__(self) -> Iterator[Any]:
        # `self`, not the raw generator: an element parked by `has_next` would
        # otherwise be skipped by whatever iterated next.
        return self

    def iter(self) -> Map:
        return self

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import to_boolean

        return to_boolean(self is other)

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if self is other else true

    def __str__(self) -> str:
        return "<map>"

    __repr__ = __str__


cloak(Map, "map")
