import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer


class _ReturnRewriter(ast.NodeTransformer):
    """Make every method answer a POOP value, never raw Python `None`.

    A method that falls off the end or uses a bare `return` answers
    CPython's implicit `None` — a raw `NoneType` on which `.is_none()`,
    `.print()`, `.if_none(...)` all crash. Rewrite bare `return` to
    `return _poop_none` and append `return _poop_none` when a function
    body does not already end in a `return`/`raise`.

    `__init__` is skipped: CPython raises `TypeError: __init__() should
    return None` for a non-`None` return, and POOP's `none` is not raw
    `None`. Generators cannot occur (`no_yield`), and loops/`if`/`with`
    are forbidden, so a `return` is always a direct body statement and an
    appended trailing return is unreachable when the body already returns.
    """

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        return self._rewrite_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        return self._rewrite_function(node)

    def _rewrite_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> ast.AST:
        # Process nested functions/classes first.
        self.generic_visit(node)
        if node.name == "__init__":
            return node
        for stmt in node.body:
            if isinstance(stmt, ast.Return) and stmt.value is None:
                stmt.value = ast.copy_location(
                    ast.Name(id="_poop_none", ctx=ast.Load()), stmt
                )
        last = node.body[-1] if node.body else None
        if not isinstance(last, (ast.Return, ast.Raise)):
            node.body.append(
                ast.Return(value=ast.Name(id="_poop_none", ctx=ast.Load()))
            )
        return node


class ReturnTransformer(BaseTransformer):
    """Rewrites implicit/bare returns to answer POOP `none`.

    The `_poop_none` binding is provided by `NoneTransformer`.
    """

    rewriter = _ReturnRewriter
    BINDINGS: ClassVar[dict[str, object]] = {}
