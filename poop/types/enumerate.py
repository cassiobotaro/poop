import builtins as _builtins
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterable_mixin import _IterableMixin
from poop.types.int import Int
from poop.types.object import Object
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.boolean import Boolean


class Enumerate(_IterableMixin, Object):
    __slots__ = ("_source", "_start")

    def __init__(self, source: Any, start: Int | None = None) -> None:
        self._source = source
        self._start: Int = Int(0) if start is None else start

    def __iter__(self) -> Iterator[Tuple]:
        for i, item in _builtins.enumerate(self._source, self._start._value):
            yield Tuple(Int(i), item)

    def __eq__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return true if self is other else false

    def __ne__(self, other: object) -> Boolean:
        from poop.types.boolean import false, true

        return false if self is other else true

    def __str__(self) -> str:
        return f"<enumerate object, start={self._start._value}>"

    __repr__ = __str__
