import builtins
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from poop.types._iterator_base import _LazyView
from poop.types._unwrap import _unwrap
from poop.types.int import Int
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.none import NoneClass


class Enumerate(_LazyView[Tuple], name="enumerate"):
    __slots__ = ("_source", "_start")

    def __init__(self, source: Any, start: Int | NoneClass | None = None) -> None:
        super().__init__()
        iter(source)
        self._source = source
        self._start: Int = Int(_unwrap(start, 0))

    @staticmethod
    def _gen(source: Any, start: int) -> Iterator[Tuple]:
        for i, item in builtins.enumerate(source, start):
            yield Tuple(Int(i), item)

    def _generate(self) -> Iterator[Tuple]:
        source = self._source
        self._source = None
        return self._gen(source, self._start._value)
