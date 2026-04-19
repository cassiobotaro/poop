import ast
from typing import ClassVar

from poop.types.float import Float


class FloatTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_float": Float}

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _FloatRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _FloatRewriter(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, float):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_float", ctx=ast.Load()),
                    args=[node],
                    keywords=[],
                ),
                node,
            )
        return node
