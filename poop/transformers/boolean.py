import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.boolean import Boolean, false, true


def _poop_bool_from(value: object = None) -> Boolean:
    if isinstance(value, Boolean):
        return value
    return true if bool(value) else false


class _BooleanRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "bool":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_bool_from", ctx=ast.Load()),
                    args=node.args,
                    keywords=[],
                ),
                node,
            )
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if node.value is True:
            return ast.copy_location(ast.Name(id="_poop_true", ctx=ast.Load()), node)
        if node.value is False:
            return ast.copy_location(ast.Name(id="_poop_false", ctx=ast.Load()), node)
        return node


class BooleanTransformer(BaseTransformer):
    rewriter = _BooleanRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_true": true,
        "_poop_false": false,
        "_poop_bool_from": _poop_bool_from,
    }
