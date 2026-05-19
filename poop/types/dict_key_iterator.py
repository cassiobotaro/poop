from typing import final

from poop.types._iterator_base import _IteratorBase
from poop.types.object import Object


@final
class DictKeyIterator(_IteratorBase[Object], name="dict_keyiterator"):
    __slots__ = ()
