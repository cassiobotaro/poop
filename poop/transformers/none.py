import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.none import none


class _NoneRewriter(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if node.value is None:
            return ast.copy_location(ast.Name(id="_poop_none", ctx=ast.Load()), node)
        return node


class NoneTransformer(BaseTransformer):
    rewriter = _NoneRewriter
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_none": none}
