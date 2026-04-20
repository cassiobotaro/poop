import ast
from typing import ClassVar

from poop.types.int import Int


class IntTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_int": Int}

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _IntRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _IntRewriter(ast.NodeTransformer):
    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        if isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant):
            if isinstance(node.operand.value, int) and not isinstance(
                node.operand.value, bool
            ):
                collapsed = ast.copy_location(
                    ast.Constant(value=-node.operand.value), node
                )
                return ast.copy_location(
                    ast.Call(
                        func=ast.Name(id="_poop_int", ctx=ast.Load()),
                        args=[collapsed],
                        keywords=[],
                    ),
                    node,
                )
        return self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, int) and not isinstance(node.value, bool):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_int", ctx=ast.Load()),
                    args=[node],
                    keywords=[],
                ),
                node,
            )
        return node
