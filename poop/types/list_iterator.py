from typing import final

from poop.types._iterator_base import _IteratorBase
from poop.types.object import Object


@final
class ListIterator(_IteratorBase[Object], name="list_iterator"):
    __slots__ = ()
