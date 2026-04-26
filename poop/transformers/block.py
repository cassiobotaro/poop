import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.block import Block


class _BlockRewriter(ast.NodeTransformer):
    def visit_Lambda(self, node: ast.Lambda) -> ast.AST:
        self.generic_visit(node)
        return ast.copy_location(
            ast.Call(
                func=ast.Name(id="_poop_block", ctx=ast.Load()),
                args=[node],
                keywords=[],
            ),
            node,
        )


class BlockTransformer(BaseTransformer):
    rewriter = _BlockRewriter
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_block": Block}
