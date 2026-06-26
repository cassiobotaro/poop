import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.slice import Slice


class _SliceRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Name) and node.func.id == "slice":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_slice", ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[
                        ast.keyword(arg=kw.arg, value=self.visit(kw.value))
                        for kw in node.keywords
                    ],
                ),
                node,
            )
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "slice":
            return ast.copy_location(ast.Name(id="_poop_slice", ctx=node.ctx), node)
        return node


class SliceTransformer(BaseTransformer):
    rewriter = _SliceRewriter
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_slice": Slice}
