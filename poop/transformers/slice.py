import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.slice import Slice


class _SliceRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "slice":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_slice", ctx=ast.Load()),
                    args=node.args,
                    keywords=node.keywords,
                ),
                node,
            )
        return node


class SliceTransformer(BaseTransformer):
    rewriter = _SliceRewriter
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_slice": Slice}
