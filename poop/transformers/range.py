import ast
from poop.transformers.base import BaseTransformer
from typing import ClassVar

from poop.types.int import Int
from poop.types.interval import Interval


def _poop_range(
    stop_or_start: Int, stop: Int | None = None, step: Int | None = None
) -> Interval:
    if stop is None:
        return Interval(Int(0), Int(int(stop_or_start) - 1), Int(1))
    if step is None:
        return Interval(Int(int(stop_or_start)), Int(int(stop) - 1), Int(1))
    return Interval(Int(int(stop_or_start)), Int(int(stop) - 1), Int(int(step)))

class _RangeRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "range":
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_range", ctx=ast.Load()),
                    args=node.args,
                    keywords=node.keywords,
                ),
                node,
            )
        return node



class RangeTransformer(BaseTransformer):
    rewriter = _RangeRewriter
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_range": _poop_range}



