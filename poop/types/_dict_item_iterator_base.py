from typing import TYPE_CHECKING

from poop.types._iterator_base import _IteratorBase
from poop.types.tuple import Tuple

if TYPE_CHECKING:
    from collections.abc import Iterable

    from poop.types.object import Object


class _DictItemIteratorBase(_IteratorBase[Tuple], name="object"):
    """Shared base for the forward and reverse dict item iterators.

    Both re-wrap raw (k, v) pairs from the underlying Python iterator into
    POOP Tuples — the one thing the plain ``_IteratorBase`` (which yields
    its elements untouched) does not do. Wrapped on the way *into* the
    cursor, one pair at a time as the underlying iterator is pulled, so the
    element `has_next` parks is already a `Tuple` and a peeked pair is never
    delivered raw. Concrete leaves are ``@final`` and differ only by their
    ``name=`` repr token; this base is never instantiated directly, so it
    keeps ``_IteratorBase``'s default name.
    """

    __slots__ = ()

    def __init__(self, pairs: Iterable[tuple[Object, Object]]) -> None:
        super().__init__(Tuple(k, v) for k, v in pairs)
