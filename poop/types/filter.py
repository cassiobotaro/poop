from collections.abc import Callable, Iterator
from typing import Any

from poop.types._iterator_base import _LazyView
from poop.types.exceptions import MIRRORS


class Filter(_LazyView[Any], name="filter"):
    __slots__ = ("_block", "_source")

    def __init__(self, source: Any, block: Callable[[Any], Any]) -> None:
        super().__init__()
        self._source = source
        self._block = block

    @staticmethod
    def _gen(source: Any, block: Any) -> Iterator[Any]:
        for item in source:
            # Caught before it can leave the generator. PEP 479 would
            # otherwise rewrite it into `RuntimeError: generator raised
            # StopIteration` — a report about a construct POOP does not have
            # and `no_yield` bans, read by someone who never wrote one. What
            # PEP 479 is *protecting* against stays protected: letting the
            # StopIteration through would end the view early and answer a
            # quietly truncated collection.
            try:
                value = block(item)
            except StopIteration:
                raise MIRRORS["RuntimeError"](
                    "a block ran off the end of an iterator — "
                    "ask #has_next before #next"
                ) from None
            if bool(value):
                yield item

    def _generate(self) -> Iterator[Any]:
        source, block = self._source, self._block
        self._source = self._block = None
        return self._gen(source, block)
