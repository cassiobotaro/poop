from typing import final

from poop.types._iterator_base import _IteratorBase
from poop.types.object import Object


@final
class SetIterator(_IteratorBase[Object], name="set_iterator"):
    __slots__ = ()
