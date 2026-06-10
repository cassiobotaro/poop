import ast
from collections.abc import Iterable
from typing import ClassVar, cast

from poop.transformers.base import BaseTransformer
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.int import Int


def _poop_bytearray_from(arg: object = None) -> ByteArray:
    if arg is None:
        return ByteArray()
    if isinstance(arg, Bytes):
        return ByteArray(arg._value)
    if isinstance(arg, Int):
        return ByteArray(bytearray(arg._value))
    if isinstance(arg, Iterable):
        ints = cast("Iterable[Int]", arg)
        return ByteArray(item._value for item in ints)
    raise TypeError(f"cannot convert {type(arg).__qualname__} to ByteArray")


class _ByteArrayRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "bytearray"
            and not node.keywords
            and len(node.args) <= 1
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_bytearray_from", ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[],
                ),
                node,
            )
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "bytearray":
            return ast.copy_location(ast.Name(id="_poop_bytearray", ctx=node.ctx), node)
        return node


class ByteArrayTransformer(BaseTransformer):
    rewriter = _ByteArrayRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_bytearray": ByteArray,
        "_poop_bytearray_from": _poop_bytearray_from,
    }
