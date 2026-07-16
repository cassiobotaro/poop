import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.exceptions import MIRRORS

_BINDINGS: dict[str, object] = {
    f"_poop_{name}": mirror for name, mirror in MIRRORS.items()
}


class _ExceptionRewriter(ast.NodeTransformer):
    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id in MIRRORS:
            return ast.copy_location(
                ast.Name(id=f"_poop_{node.id}", ctx=node.ctx), node
            )
        return node


class ExceptionTransformer(BaseTransformer):
    """Rewrites exception names to POOP's mirrors.

    Rewrites:
        Try(...).except_(ValueError, h)  → ...except_(_poop_ValueError, h)
        ValueError.raise_("boom")        → _poop_raise(_poop_ValueError, "boom")
        class MyError(Exception):        → class MyError(_poop_Exception):

    A transformer rather than a `DEFAULT_NAMESPACE` entry: the namespace is
    exactly `Try` and `With`, and every other builtin reaches user code by
    being rewritten to a mangled name. Same shape the Ellipsis transformer
    uses.

    **Must run after `RaiseTransformer`.** That one matches an uppercase
    `ast.Name` followed by `.raise_(...)`; rewriting `ValueError` to
    `_poop_ValueError` first would leave a name starting with an underscore
    and silently stop `raise_` from being recognised at all.
    """

    rewriter = _ExceptionRewriter
    BINDINGS: ClassVar[dict[str, object]] = _BINDINGS
