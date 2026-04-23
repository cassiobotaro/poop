import ast
from typing import ClassVar

from poop.types.float import Float


def _poop_float_from(value: object = None) -> Float:
    from poop.types.int import Int
    from poop.types.string import Str

    if value is None:
        return Float(0.0)
    if isinstance(value, Float):
        return value
    if isinstance(value, Int):
        return Float(float(value._value))
    if isinstance(value, Str):
        return Float(float(value._value))
    raise TypeError(f"cannot convert {type(value).__name__} to Float")


class FloatTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_float": Float,
        "_poop_float_from": _poop_float_from,
    }

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _FloatRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _FloatRewriter(ast.NodeTransformer):
    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        if isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant):
            if isinstance(node.operand.value, float):
                collapsed = ast.copy_location(
                    ast.Constant(value=-node.operand.value), node
                )
                return ast.copy_location(
                    ast.Call(
                        func=ast.Name(id="_poop_float", ctx=ast.Load()),
                        args=[collapsed],
                        keywords=[],
                    ),
                    node,
                )
        return self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "float":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_float_from", ctx=ast.Load()),
                    args=node.args,
                    keywords=[],
                ),
                node,
            )
        return node

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
