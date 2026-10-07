import builtins
from typing import TYPE_CHECKING, Any

from poop.types._argument import a_collection, an_int
from poop.types._iterator_base import _LazyView
from poop.types.int import Int
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from collections.abc import Iterator

    from poop.types.none import NoneClass


class Enumerate(_LazyView[Tuple], name="enumerate"):
    __slots__ = ("_source", "_start")

    def __init__(self, source: Any, start: Int | NoneClass | None = None) -> None:
        super().__init__()
        a_collection(source, "enumerate")
        self._source = source
        # Guarded here, not on the first walk: a wrong `start` used to be
        # wrapped in an `Int` as is and refused by CPython only when walked.
        self._start: Int = Int(an_int(start, "enumerate", "start", 0))

    @staticmethod
    def _gen(source: Any, start: int) -> Iterator[Tuple]:
        for i, item in builtins.enumerate(source, start):
            yield Tuple(Int(i), item)

    def _generate(self) -> Iterator[Tuple]:
        source = self._source
        self._source = None
        return self._gen(source, self._start._value)
