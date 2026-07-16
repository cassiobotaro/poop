from collections import deque
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from poop.types._iterator_base import _MISSING, _IteratorBase
from poop.types.none import none
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.none import NoneClass


class _DictItemIteratorBase(_IteratorBase[Tuple]):
    """Shared base for the forward and reverse dict item iterators.

    Both re-wrap raw (k, v) pairs from the underlying Python iterator into
    POOP Tuples — the one thing the plain ``_IteratorBase`` (which yields
    its elements untouched) does not do. Concrete leaves are ``@final`` and
    differ only by their ``name=`` repr token; this base is never
    instantiated directly, so it keeps ``_IteratorBase``'s default name.
    """

    __slots__ = ()

    def next(self, default: Any = _MISSING) -> Tuple:
        try:
            k, v = next(self._iter)
        except StopIteration:
            if default is not _MISSING:
                return default
            raise
        return Tuple(k, v)

    def __next__(self) -> Tuple:
        return self.next()

    def do(self, block: Callable[[Tuple], Any]) -> NoneClass:
        deque((block(Tuple(k, v)) for k, v in self._iter), maxlen=0)
        return none
