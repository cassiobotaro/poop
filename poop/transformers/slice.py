import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.slice import Slice


class _SliceRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if isinstance(node.func, ast.Name) and node.func.id == "slice":
            args = [self.visit(arg) for arg in node.args]
            # CPython's one-argument `slice(stop)` means `slice(None, stop,
            # None)` — the lone argument is the stop, not the start. Slice(...)
            # binds positionals as (start, stop, step), so a bare `slice(x)`
            # would wrongly make x the start; inject the implicit None start to
            # mirror the builtin (NoneTransformer has already run, so a raw
            # `None` constant reaches Slice, whose _coerce maps it to None).
            if len(args) == 1 and not node.keywords:
                args.insert(0, ast.Constant(value=None))
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_slice", ctx=ast.Load()),
                    args=args,
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
        if node.id == "slice":
            return ast.copy_location(ast.Name(id="_poop_slice", ctx=node.ctx), node)
        return node


class SliceTransformer(BaseTransformer):
    rewriter = _SliceRewriter
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_slice": Slice}
