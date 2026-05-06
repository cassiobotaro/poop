from collections import deque
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, final

from poop.types._iterator_base import _IteratorBase
from poop.types.none import none
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from poop.types.none import NoneClass


@final
class DictItemIterator(_IteratorBase):
    __slots__ = ()

    def next(self) -> Tuple:
        k, v = next(self._iter)
        return Tuple(k, v)

    def do(self, block: Callable[[Tuple], Any]) -> NoneClass:
        deque((block(Tuple(k, v)) for k, v in self._iter), maxlen=0)
        return none

    def __str__(self) -> str:
        return "<dict_itemiterator>"

    __repr__ = __str__
