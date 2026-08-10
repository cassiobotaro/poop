import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types._alias import builtin_alias
from poop.types.boolean import Boolean
from poop.types.exceptions import MIRRORS
from poop.types.float import Float
from poop.types.int import Int
from poop.types.string import Str


def _parsed(value: Str, base: int | None) -> Int:
    """`int(text)` / `int(text, base)`, reworded.

    CPython answers `invalid literal for int() with base 10: 'abc'` — a Python
    call, plus a base the reader never passed — and `int() base must be >= 2
    and <= 36, or 0`, naming the same call again.

    The base is checked here rather than read back out of CPython's message:
    that message says `base` too, so telling the two failures apart by their
    text would have made `int("abc")` answer the base's error.
    """
    if base is not None and base != 0 and not 2 <= base <= 36:
        raise MIRRORS["ValueError"]("int base must be 0, or between 2 and 36")
    try:
        return Int(int(value._value, 10 if base is None else base))
    except ValueError:
        in_base = "" if base is None else f" in base {base}"
        raise MIRRORS["ValueError"](
            f"{value._value!r} is not a valid int{in_base}"
        ) from None


def _poop_int_from(value: object = None, base: object = None) -> Int:
    if base is not None and not isinstance(value, Str):
        # Mirror CPython: a base is meaningful only when parsing a string.
        # int(10, 2) / int(3.5, 2) / int(True, 2) all raise TypeError there;
        # silently dropping the base would diverge from the language.
        raise MIRRORS["TypeError"]("a base applies only to text")
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
            return _parsed(value, base._value)
        return _parsed(value, None)
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
            return ast.copy_location(ast.Name(id="_poop_int_cls", ctx=node.ctx), node)
        return node


class IntTransformer(BaseTransformer):
    rewriter = _IntRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_int": Int,
        "_poop_int_cls": builtin_alias(Int, _poop_int_from, "int"),
        "_poop_int_from": _poop_int_from,
    }
