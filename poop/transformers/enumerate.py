import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.enumerate import Enumerate
from poop.types.int import Int


def _poop_enumerate(source: object, start: Int | None = None) -> Enumerate:
    return Enumerate(source, start)


class _EnumerateRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Name) and node.func.id == "enumerate":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_enumerate", ctx=ast.Load()),
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
        if node.id == "enumerate":
            return ast.copy_location(ast.Name(id="Enumerate", ctx=node.ctx), node)
        return node


class EnumerateTransformer(BaseTransformer):
    rewriter = _EnumerateRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_enumerate": _poop_enumerate,
        "Enumerate": Enumerate,
    }
