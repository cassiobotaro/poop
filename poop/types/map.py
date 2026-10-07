from typing import TYPE_CHECKING, Any

from poop.types._block_view import _BlockView

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


class Map(_BlockView, name="map"):
    __slots__ = ()

    @staticmethod
    def _gen(source: Any, block: Callable[[Any], Any]) -> Iterator[Any]:
        return (_BlockView._call(block, item) for item in source)
