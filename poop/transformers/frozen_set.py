from typing import ClassVar

from poop.transformers._collection import CollectionRewriter, make_iterable_from
from poop.transformers.base import BaseTransformer
from poop.types.frozen_set import FrozenSet

# Share the collection conversion machinery so frozenset(x) rejects a
# non-iterable with the same clean "cannot convert int to frozenset"
# message as set/list/tuple, instead of leaking Python's raw type name
# and the internal "argument after * must be an iterable" wording.
# frozenset is immutable, so (like tuple) a FrozenSet argument is
# returned unchanged rather than copied.
_poop_frozenset_from = make_iterable_from(FrozenSet)


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
