import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer, call_at
from poop.types.block import Block


class _BlockRewriter(ast.NodeTransformer):
    def visit_Lambda(self, node: ast.Lambda) -> ast.AST:
        self.generic_visit(node)
        return call_at("_poop_block", [node], node)


class BlockTransformer(BaseTransformer):
    rewriter = _BlockRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_block": Block,
    }
