import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.memory_view import MemoryView


def _poop_memoryview_from(arg: object = None) -> MemoryView:
    if isinstance(arg, Bytes):
        return MemoryView(memoryview(arg._value))
    if isinstance(arg, ByteArray):
        return MemoryView(memoryview(arg._value))
    return MemoryView(memoryview(b""))


class _MemoryViewRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "memoryview"
            and not node.keywords
            and len(node.args) == 1
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_memoryview_from", ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[],
                ),
                node,
            )
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "memoryview":
            return ast.copy_location(ast.Name(id="MemoryView", ctx=node.ctx), node)
        return node


class MemoryViewTransformer(BaseTransformer):
    rewriter = _MemoryViewRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_memoryview_from": _poop_memoryview_from,
        "MemoryView": MemoryView,
    }
