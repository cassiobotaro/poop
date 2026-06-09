import ast
from typing import ClassVar

from poop.transformers._collection import (
    CollectionRewriter,
    make_constructor,
    make_iterable_from,
    wrap_elts,
)
from poop.transformers.base import BaseTransformer
from poop.types.list import List

_poop_list = make_constructor(List)
_poop_list_from = make_iterable_from(List, "List")


class _ListRewriter(CollectionRewriter):
    builtin = "list"
    call_target = "_poop_list_from"
    name_target = "_poop_list_cls"

    def visit_List(self, node: ast.List) -> ast.AST:
        self.generic_visit(node)
        if not isinstance(node.ctx, ast.Load):
            return node
        return wrap_elts(node, "_poop_list")


class ListTransformer(BaseTransformer):
    rewriter = _ListRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_list": _poop_list,
        "_poop_list_from": _poop_list_from,
        "_poop_list_cls": List,
    }
