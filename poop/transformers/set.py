import ast
from typing import ClassVar

from poop.transformers._collection import (
    CollectionRewriter,
    make_constructor,
    make_iterable_from,
    wrap_elts,
)
from poop.transformers.base import BaseTransformer
from poop.types.set import Set

_poop_set = make_constructor(Set)
_poop_set_from = make_iterable_from(Set, copy=True)


class _SetRewriter(CollectionRewriter):
    builtin = "set"
    call_target = "_poop_set_from"
    name_target = "_poop_set_cls"

    def visit_Set(self, node: ast.Set) -> ast.AST:
        self.generic_visit(node)
        return wrap_elts(node, "_poop_set")


class SetTransformer(BaseTransformer):
    rewriter = _SetRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_set": _poop_set,
        "_poop_set_from": _poop_set_from,
        "_poop_set_cls": Set,
    }
