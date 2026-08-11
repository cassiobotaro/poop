import ast
from typing import ClassVar

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer
from poop.types._alias import builtin_alias
from poop.types.boolean import Boolean
from poop.types.exceptions import MIRRORS
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str


def _poop_float_from(*args: object, **kwargs: object) -> Float:
    refuse_extra_arguments(
        "float",
        args,
        kwargs,
        most=1,
        built_from="at most one number or string",
        hint="write a literal for a value",
    )
    value = args[0] if args else None
    if value is None:
        return Float(0.0)
    if isinstance(value, Float):
        return value
    if isinstance(value, Boolean):
        # CPython's float(True) -> 1.0 / float(False) -> 0.0.
        return Float(1.0 if bool(value) else 0.0)
    if isinstance(value, Int):
        return Float(float(value._value))
    if isinstance(value, Str):
        try:
            return Float(float(value._value))
        except ValueError:
            # `could not convert string to float: 'abc'` names Python's type,
            # not the message the reader sent.
            raise MIRRORS["ValueError"](
                f"{value._value!r} is not a valid float"
            ) from None
    raise MIRRORS["TypeError"](f"cannot convert {type(value).__name__} to float")


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
        # `not node.keywords`: see the twin guard in `boolean.py`. Rewritten
        # unconditionally, `float(x=1)` answered `0.0` off the helper's
        # default instead of CPython's `float() takes no keyword arguments`.
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "float"
            and not node.keywords
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_float_from", ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[],
                ),
                node,
            )
        self.generic_visit(node)
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

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "float":
            return ast.copy_location(ast.Name(id="_poop_float_cls", ctx=node.ctx), node)
        return node


class FloatTransformer(BaseTransformer):
    rewriter = _FloatRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_float": Float,
        "_poop_float_cls": builtin_alias(Float, _poop_float_from, "float"),
        "_poop_float_from": _poop_float_from,
    }
