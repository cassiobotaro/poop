import builtins
from typing import TYPE_CHECKING

from poop.types._argument import a_collection, an_int
from poop.types._iterator_base import _LazyView
from poop.types.int import Int
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from poop.types.none import NoneClass
    from poop.types.object import Object


class Enumerate(_LazyView[Tuple], name="enumerate"):
    __slots__ = ("_source", "_start")

    def __init__(self, source: object, start: Int | NoneClass | None = None) -> None:
        super().__init__()
        self._source: Iterable[Object] = a_collection(source, "enumerate")
        # Guarded here, not on the first walk: a wrong `start` used to be
        # wrapped in an `Int` as is and refused by CPython only when walked.
        self._start: Int = Int(an_int(start, "enumerate", "start", 0))

    @staticmethod
    def _gen(source: Iterable[Object], start: int) -> Iterator[Tuple]:
        for i, item in builtins.enumerate(source, start):
            yield Tuple(Int(i), item)

    def _generate(self) -> Iterator[Tuple]:
        source = self._source
        del self._source
        return self._gen(source, self._start._value)
