import ast
from collections.abc import Iterable
from typing import ClassVar, cast

from poop.transformers.base import BaseTransformer
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.string import Str


def _poop_bytes_from(arg: object = None, encoding: object = None) -> Bytes:
    if arg is None:
        return Bytes(b"")
    if isinstance(arg, Bytes):
        return arg
    if isinstance(arg, Int):
        return Bytes(bytes(arg._value))
    if isinstance(arg, Str):
        enc = encoding._value if isinstance(encoding, Str) else "utf-8"
        return Bytes(arg._value.encode(enc))
    if isinstance(arg, Iterable):
        ints = cast("Iterable[Int]", arg)
        return Bytes(bytes(item._value for item in ints))
    raise TypeError(f"cannot convert {type(arg).__name__} to Bytes")


class _BytesRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "bytes"
            and not node.keywords
            and len(node.args) <= 2
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_bytes_from", ctx=ast.Load()),
                    args=node.args,
                    keywords=[],
                ),
                node,
            )
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, bytes):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_bytes", ctx=ast.Load()),
                    args=[node],
                    keywords=[],
                ),
                node,
            )
        return node


class BytesTransformer(BaseTransformer):
    rewriter = _BytesRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_bytes": Bytes,
        "_poop_bytes_from": _poop_bytes_from,
    }
