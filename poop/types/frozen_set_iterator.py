from typing import final

from poop.types._iterator_base import _IteratorBase
from poop.types.object import Object


@final
class FrozenSetIterator(_IteratorBase[Object], name="frozenset_iterator"):
    __slots__ = ()
