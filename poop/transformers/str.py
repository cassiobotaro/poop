import ast
from typing import ClassVar

from poop.types.str import Str


class StrTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_str": Str}

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _StrRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _StrRewriter(ast.NodeTransformer):
    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, str):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_str", ctx=ast.Load()),
                    args=[node],
                    keywords=[],
                ),
                node,
            )
        return node
