import ast

from poop.transformers._collection import LiteralRewriter, make_iterable_from
from poop.transformers.base import BaseTransformer
from poop.types._alias import builtin_alias
from poop.types.set import Set

_poop_set_from = make_iterable_from(Set, copy=True)


class _SetRewriter(LiteralRewriter):
    builtin = "set"
    call_target = "_poop_set_from"
    name_target = "_poop_set_cls"
    literal_node = ast.Set
    literal_target = "_poop_set"


class SetTransformer(BaseTransformer):
    rewriter = _SetRewriter
    BINDINGS = {
        # The class itself: its `__init__` is variadic, which is the shape a
        # literal's elements arrive in.
        "_poop_set": Set,
        "_poop_set_from": _poop_set_from,
        "_poop_set_cls": builtin_alias(Set, _poop_set_from, "set"),
    }
