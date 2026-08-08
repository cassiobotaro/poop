from collections import deque
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from poop.types._cloak import cloak
from poop.types._iterator_base import _IteratorBase
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

    def _wrap(self, value: Any) -> Tuple:
        k, v = value
        return Tuple(k, v)

    def do(self, block: Callable[[Tuple], Any]) -> NoneClass:
        # Through `self`, not `self._iter`: a pair parked by `has_next` would
        # otherwise be skipped, and would arrive unwrapped if it were not.
        deque((block(item) for item in self), maxlen=0)
        return none


# Cloaked as `object`, the root's own spelling: these methods are inherited by
# many wrappers, so no single builtin name is true for all of them — and left
# alone CPython blamed `_DictItemIteratorBase` in every wrong-arity message, a private name
# `_reject_private` exists to keep out of user code.
cloak(_DictItemIteratorBase, "object")
