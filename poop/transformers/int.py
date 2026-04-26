import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.int import Int


def _poop_int_from(value: object = None, base: object = None) -> Int:
    from poop.types.float import Float
    from poop.types.string import Str

    if value is None:
        return Int(0)
    if isinstance(value, Int):
        return value
    if isinstance(value, Float):
        return Int(int(value._value))
    if isinstance(value, Str):
        if base is not None:
            if not isinstance(base, Int):
                raise TypeError(f"base must be Int, got {type(base).__name__}")
            return Int(int(value._value, base._value))
        return Int(int(value._value))
    raise TypeError(f"cannot convert {type(value).__name__} to Int")


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

    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "int":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_int_from", ctx=ast.Load()),
                    args=node.args,
                    keywords=node.keywords,
                ),
                node,
            )
        return node

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


class IntTransformer(BaseTransformer):
    rewriter = _IntRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_int": Int,
        "_poop_int_from": _poop_int_from,
    }
