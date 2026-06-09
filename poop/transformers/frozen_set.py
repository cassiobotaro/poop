from collections.abc import Iterable
from typing import TYPE_CHECKING, ClassVar

from poop.transformers._collection import CollectionRewriter
from poop.transformers.base import BaseTransformer
from poop.types.frozen_set import FrozenSet

if TYPE_CHECKING:
    from poop.types.object import Object


def _poop_frozenset_from(iterable: Iterable[Object] | None = None) -> FrozenSet:
    if iterable is not None:
        return FrozenSet(*iterable)
    return FrozenSet()


class _FrozenSetRewriter(CollectionRewriter):
    builtin = "frozenset"
    call_target = "_poop_frozenset_from"
    name_target = "_poop_frozenset"


class FrozenSetTransformer(BaseTransformer):
    rewriter = _FrozenSetRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_frozenset": FrozenSet,
        "_poop_frozenset_from": _poop_frozenset_from,
    }
