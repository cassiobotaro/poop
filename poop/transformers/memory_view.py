import ast
from typing import ClassVar

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer
from poop.types._alias import builtin_alias
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.exceptions import MIRRORS
from poop.types.memory_view import MemoryView


def _poop_memoryview_from(*args: object, **kwargs: object) -> MemoryView:
    refuse_extra_arguments(
        "memoryview",
        args,
        kwargs,
        most=1,
        built_from="exactly one bytes-like object",
        hint="write memoryview(b) over the buffer you mean",
    )
    arg = args[0] if args else None
    if isinstance(arg, Bytes):
        return MemoryView(memoryview(arg._value))
    if isinstance(arg, ByteArray):
        return MemoryView(memoryview(arg._value))
    raise MIRRORS["TypeError"](
        f"memoryview: a bytes-like object is required, not {type(arg).__qualname__}"
    )


class _MemoryViewRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Name) and node.func.id == "memoryview":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_memoryview_from", ctx=ast.Load()),
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
        if node.id == "memoryview":
            return ast.copy_location(
                ast.Name(id="_poop_memoryview_cls", ctx=node.ctx), node
            )
        return node


class MemoryViewTransformer(BaseTransformer):
    rewriter = _MemoryViewRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_memoryview": MemoryView,
        "_poop_memoryview_cls": builtin_alias(
            MemoryView, _poop_memoryview_from, "memoryview"
        ),
        "_poop_memoryview_from": _poop_memoryview_from,
    }
