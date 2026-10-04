import ast

from poop.transformers.base import BaseTransformer, name_at
from poop.types.none import none


class _NoneRewriter(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if node.value is None:
            return name_at("_poop_none", node)
        return node


class NoneTransformer(BaseTransformer):
    rewriter = _NoneRewriter
    BINDINGS = {"_poop_none": none}
