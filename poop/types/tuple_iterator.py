from typing import final

from poop.types._iterator_base import _IteratorBase
from poop.types.object import Object


@final
class TupleIterator(_IteratorBase[Object], name="tuple_iterator"):
    __slots__ = ()
