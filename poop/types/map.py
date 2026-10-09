from typing import TYPE_CHECKING

from poop.types._block_view import _BlockView

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator

    from poop.types.object import Object


class Map[S: Object, T: Object](_BlockView[S, T], name="map"):
    __slots__ = ()

    @staticmethod
    def _gen(source: Iterable[S], block: Callable[[S], T]) -> Iterator[T]:
        return (_BlockView._call(block, item) for item in source)
