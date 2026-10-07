from typing import TYPE_CHECKING, Any

from poop.types._cloak import cloak
from poop.types._iterator_base import _LazyView
from poop.types.exceptions import MIRRORS

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


class _BlockView(_LazyView[Any]):
    """Base for the views that send a block to each element: `map`, `filter`.

    The two differed in one line — what the block's answer does with the
    element — and spelt the slots, the constructor, the hand-off in
    `_generate` and the guarded call to the block twice. Each view now
    supplies only `_gen`, the generator built from `(source, block)`.
    """

    __slots__ = ("_block", "_source")

    def __init__(self, source: Any, block: Callable[[Any], Any]) -> None:
        super().__init__()
        self._source = source
        self._block: Any = block

    @staticmethod
    def _call(block: Callable[[Any], Any], item: Any) -> Any:
        """`block(item)`, with a `StopIteration` it raises reworded.

        Caught before it can leave the generator. PEP 479 would otherwise
        rewrite it into `RuntimeError: generator raised StopIteration` — a
        report about a construct POOP does not have and `no_yield` bans, read
        by someone who never wrote one. What PEP 479 is *protecting* against
        stays protected: letting the StopIteration through would end the view
        early and answer a quietly truncated collection.
        """
        try:
            return block(item)
        except StopIteration:
            raise MIRRORS["RuntimeError"](
                "a block ran off the end of an iterator — ask #has_next before #next"
            ) from None

    @staticmethod
    def _gen(source: Any, block: Callable[[Any], Any]) -> Iterator[Any]:
        raise NotImplementedError

    def _generate(self) -> Iterator[Any]:
        source, block = self._source, self._block
        self._source = self._block = None
        return self._gen(source, block)


# Cloaked as `object`, as `_LazyView` is: its members are inherited by both
# views, so neither builtin name is true for all of them.
cloak(_BlockView, "object")
