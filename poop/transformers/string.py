import ast
from typing import ClassVar

from poop.types.string import Str


def _poop_str_from(value: object = None) -> Str:
    if value is None:
        return Str("")
    if isinstance(value, Str):
        return value
    return Str(str(value))


class StrTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_str": Str,
        "_poop_str_from": _poop_str_from,
    }

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _StrRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _StrRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "str":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_str_from", ctx=ast.Load()),
                    args=node.args,
                    keywords=[],
                ),
                node,
            )
        return node

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
