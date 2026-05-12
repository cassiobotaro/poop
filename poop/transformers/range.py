import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.int import Int
from poop.types.range import Range


def _poop_range(
    stop_or_start: Int, stop: Int | None = None, step: Int | None = None
) -> Range:
    if stop is None:
        return Range(Int(0), Int(int(stop_or_start) - 1), Int(1))
    if step is None:
        return Range(Int(int(stop_or_start)), Int(int(stop) - 1), Int(1))
    step_value = int(step)
    sign = 1 if step_value > 0 else -1
    return Range(Int(int(stop_or_start)), Int(int(stop) - sign), Int(step_value))


class _RangeRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Name) and node.func.id == "range":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_range", ctx=ast.Load()),
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
        if node.id == "range":
            return ast.copy_location(ast.Name(id="_poop_range_cls", ctx=node.ctx), node)
        return node


class RangeTransformer(BaseTransformer):
    rewriter = _RangeRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_range": _poop_range,
        "_poop_range_cls": Range,
    }
