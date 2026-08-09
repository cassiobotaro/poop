import ast
from collections.abc import Iterable
from typing import ClassVar, cast

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.exceptions import MIRRORS
from poop.types.int import Int


def _poop_bytearray_from(*args: object, **kwargs: object) -> ByteArray:
    refuse_extra_arguments(
        "bytearray",
        args,
        kwargs,
        most=1,
        built_from="at most one source",
        hint='write bytearray(b"…") to copy bytes',
    )
    arg = args[0] if args else None
    if arg is None:
        return ByteArray()
    if isinstance(arg, Bytes):
        return ByteArray(arg._value)
    if isinstance(arg, Int):
        return ByteArray(bytearray(arg._value))
    if isinstance(arg, Iterable):
        ints = cast("Iterable[Int]", arg)
        return ByteArray(item._value for item in ints)
    raise MIRRORS["TypeError"](f"cannot convert {type(arg).__qualname__} to bytearray")


class _ByteArrayRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Name) and node.func.id == "bytearray":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_bytearray_from", ctx=ast.Load()),
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
        if node.id == "bytearray":
            return ast.copy_location(ast.Name(id="_poop_bytearray", ctx=node.ctx), node)
        return node


class ByteArrayTransformer(BaseTransformer):
    rewriter = _ByteArrayRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_bytearray": ByteArray,
        "_poop_bytearray_from": _poop_bytearray_from,
    }
