import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.boolean import Boolean
from poop.types.exceptions import MIRRORS
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str


def _poop_int_from(value: object = None, base: object = None) -> Int:
    if base is not None and not isinstance(value, Str):
        # Mirror CPython: a base is meaningful only when parsing a string.
        # int(10, 2) / int(3.5, 2) / int(True, 2) all raise TypeError there;
        # silently dropping the base would diverge from the language.
        raise MIRRORS["TypeError"]("int() can't convert non-string with explicit base")
    if value is None:
        return Int(0)
    if isinstance(value, Int):
        return value
    if isinstance(value, Boolean):
        # CPython's int(True) -> 1 / int(False) -> 0 (the flag-to-number
        # bridge). Boolean is kept out of *implicit* arithmetic, but
        # explicit conversion is sanctioned (like str(True)).
        return Int(1 if bool(value) else 0)
    if isinstance(value, Float):
        return Int(int(value._value))
    if isinstance(value, Str):
        if base is not None:
            if not isinstance(base, Int):
                raise MIRRORS["TypeError"](
                    f"base must be int, got {type(base).__name__}"
                )
            return Int(int(value._value, base._value))
        return Int(int(value._value))
    raise MIRRORS["TypeError"](f"cannot convert {type(value).__name__} to int")


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
        if isinstance(node.func, ast.Name) and node.func.id == "int":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_int_from", ctx=ast.Load()),
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

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "int":
            return ast.copy_location(ast.Name(id="_poop_int", ctx=node.ctx), node)
        return node


class IntTransformer(BaseTransformer):
    rewriter = _IntRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_int": Int,
        "_poop_int_from": _poop_int_from,
    }
