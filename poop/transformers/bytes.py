import ast
from typing import ClassVar

from poop.types.bytes import Bytes


class BytesTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_bytes": Bytes}

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _BytesRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _BytesRewriter(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, bytes):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_bytes", ctx=ast.Load()),
                    args=[node],
                    keywords=[],
                ),
                node,
            )
        return node
