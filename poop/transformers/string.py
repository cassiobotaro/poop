import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.string import Str


def _poop_str_from(value: object = None) -> Str:
    if value is None:
        return Str("")
    if isinstance(value, Str):
        return value
    return Str(str(value))


class _StrRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Name) and node.func.id == "str":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_str_from", ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[],
                ),
                node,
            )
        self.generic_visit(node)
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

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "str":
            return ast.copy_location(ast.Name(id="_poop_str", ctx=node.ctx), node)
        return node


class StrTransformer(BaseTransformer):
    rewriter = _StrRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_str": Str,
        "_poop_str_from": _poop_str_from,
    }
