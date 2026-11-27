import ast

from poop.transformers.base import BaseTransformer


class _AwaitRewriter(ast.NodeTransformer):
    """`x.await_()` becomes `await x`.

    A method cannot suspend the coroutine that sent it, so `await_` is never
    sent: the rewrite is syntax. `no_misplaced_await` has already refused
    every use this cannot honour, so each match here is a bare call directly
    inside an async method.
    """

    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "await_":
            return ast.copy_location(ast.Await(value=func.value), node)
        return node


class AwaitTransformer(BaseTransformer):
    rewriter = _AwaitRewriter
