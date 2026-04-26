import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.memory_view import MemoryView


def _poop_memoryview_from(arg: object = None) -> MemoryView:
    from poop.types.byte_array import ByteArray
    from poop.types.bytes import Bytes

    if isinstance(arg, Bytes):
        return MemoryView(memoryview(arg._value))
    if isinstance(arg, ByteArray):
        return MemoryView(memoryview(arg._value))
    return MemoryView(memoryview(b""))


class _MemoryViewRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "memoryview"
            and not node.keywords
            and len(node.args) == 1
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_memoryview_from", ctx=ast.Load()),
                    args=node.args,
                    keywords=[],
                ),
                node,
            )
        return node


class MemoryViewTransformer(BaseTransformer):
    rewriter = _MemoryViewRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_memoryview_from": _poop_memoryview_from
    }
