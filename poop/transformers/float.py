import ast
from typing import ClassVar

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter, call_at
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


class _FloatRewriter(BuiltinRewriter):
    builtin = "float"
    call_target = "_poop_float_from"
    name_target = "_poop_float_cls"

    def visit_UnaryOp(self, node: ast.UnaryOp) -> ast.AST:
        # `-5` parses as `USub(Constant(5))`; folded here so the literal is one
        # value, not a message sent to a positive one.
        if (
            isinstance(node.op, ast.USub)
            and isinstance(node.operand, ast.Constant)
            and isinstance(node.operand.value, float)
        ):
            folded = ast.copy_location(ast.Constant(value=-node.operand.value), node)
            return call_at("_poop_float", [folded], node)
        return self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, float):
            return call_at("_poop_float", [node], node)
        return node


class FloatTransformer(BaseTransformer):
    rewriter = _FloatRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_float": Float,
        "_poop_float_cls": builtin_alias(Float, _poop_float_from, "float"),
        "_poop_float_from": _poop_float_from,
    }
