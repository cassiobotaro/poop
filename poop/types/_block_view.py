from typing import TYPE_CHECKING

from poop.types._cloak import cloak
from poop.types._iterator_base import _LazyView
from poop.types.exceptions import MIRRORS

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator

    from poop.types.object import Object


class _BlockView[S: Object, T: Object](_LazyView[T]):
    """Base for the views that send a block to each element: `map`, `filter`.

    The two differed in one line — what the block's answer does with the
    element — and spelt the slots, the constructor, the hand-off in
    `_generate` and the guarded call to the block twice. Each view now
    supplies only `_gen`, the generator built from `(source, block)`.

    Generic over the source's element `S` and the view's own `T`: a `Map`
    yields what its block answers, a `Filter` what its source yields.
    """

    __slots__ = ("_block", "_source")

    def __init__(self, source: Iterable[S], block: Callable[[S], object]) -> None:
        super().__init__()
        self._source = source
        self._block = block

    @staticmethod
    def _call[A, R](block: Callable[[A], R], item: A) -> R:
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
    def _gen(source: Iterable[S], block: Callable[[S], object]) -> Iterator[T]:
        raise NotImplementedError

    def _generate(self) -> Iterator[T]:
        source, block = self._source, self._block
        # `del`, not `= None`: the slots release the source and the block the
        # same way, without widening their types to admit a `None` that only
        # ever stands for "already handed over".
        del self._source, self._block
        return self._gen(source, block)


# Cloaked as `object`, as `_LazyView` is: its members are inherited by both
# views, so neither builtin name is true for all of them.
cloak(_BlockView, "object")
