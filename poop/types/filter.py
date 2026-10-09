from typing import TYPE_CHECKING

from poop.types._block_view import _BlockView

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator

    from poop.types.object import Object


class Filter[T: Object](_BlockView[T, T], name="filter"):
    __slots__ = ()

    @staticmethod
    def _gen(source: Iterable[T], block: Callable[[T], object]) -> Iterator[T]:
        return (item for item in source if _BlockView._call(block, item))
