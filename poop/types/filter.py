from typing import TYPE_CHECKING, Any

from poop.types._block_view import _BlockView

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


class Filter(_BlockView, name="filter"):
    __slots__ = ()

    @staticmethod
    def _gen(source: Any, block: Callable[[Any], Any]) -> Iterator[Any]:
        return (item for item in source if _BlockView._call(block, item))
