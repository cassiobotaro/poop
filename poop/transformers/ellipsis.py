import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.ellipsis import ellipsis


class _EllipsisRewriter(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if node.value is Ellipsis:
            return ast.copy_location(
                ast.Name(id="_poop_ellipsis", ctx=ast.Load()), node
            )
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        # `...` and `Ellipsis` are two spellings of the same value; rewriting
        # only the literal would leave the name handing out the raw primitive.
        if node.id == "Ellipsis":
            return ast.copy_location(ast.Name(id="_poop_ellipsis", ctx=node.ctx), node)
        return node


class EllipsisTransformer(BaseTransformer):
    rewriter = _EllipsisRewriter
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_ellipsis": ellipsis}
