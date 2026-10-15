import ast

from poop.transformers._collection import LiteralRewriter, make_iterable_from
from poop.transformers.base import BaseTransformer
from poop.types._alias import builtin_alias
from poop.types.tuple import Tuple

_poop_tuple_from = make_iterable_from(Tuple)


class _TupleRewriter(LiteralRewriter):
    builtin = "tuple"
    call_target = "_poop_tuple_from"
    name_target = "_poop_tuple_cls"
    literal_node = ast.Tuple
    literal_target = "_poop_tuple"


class TupleTransformer(BaseTransformer):
    rewriter = _TupleRewriter
    BINDINGS = {
        # The class itself: its `__init__` is variadic, which is the shape a
        # literal's elements arrive in.
        "_poop_tuple": Tuple,
        "_poop_tuple_from": _poop_tuple_from,
        "_poop_tuple_cls": builtin_alias(Tuple, _poop_tuple_from, "tuple"),
    }
