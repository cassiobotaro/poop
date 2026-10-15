import ast

from poop.transformers._collection import make_iterable_from, wrap_elts
from poop.transformers.base import BaseTransformer, BuiltinRewriter
from poop.types._alias import builtin_alias
from poop.types.tuple import Tuple

_poop_tuple_from = make_iterable_from(Tuple)


class _TupleRewriter(BuiltinRewriter):
    builtin = "tuple"
    call_target = "_poop_tuple_from"
    name_target = "_poop_tuple_cls"

    def visit_Tuple(self, node: ast.Tuple) -> ast.AST:
        self.generic_visit(node)
        if not isinstance(node.ctx, ast.Load):
            return node
        return wrap_elts(node, "_poop_tuple")


class TupleTransformer(BaseTransformer):
    rewriter = _TupleRewriter
    BINDINGS = {
        # The class itself: its `__init__` is variadic, which is the shape a
        # literal's elements arrive in.
        "_poop_tuple": Tuple,
        "_poop_tuple_from": _poop_tuple_from,
        "_poop_tuple_cls": builtin_alias(Tuple, _poop_tuple_from, "tuple"),
    }
