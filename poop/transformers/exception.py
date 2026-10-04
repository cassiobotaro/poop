import ast

from poop.transformers.base import BaseTransformer, name_at
from poop.types.exceptions import MIRRORS

_BINDINGS: dict[str, object] = {
    f"_poop_{name}": mirror for name, mirror in MIRRORS.items()
}


class _ExceptionRewriter(ast.NodeTransformer):
    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id in MIRRORS:
            return name_at(f"_poop_{node.id}", node, node.ctx)
        return node


class ExceptionTransformer(BaseTransformer):
    """Rewrites exception names to POOP's mirrors.

    Rewrites:
        Try(...).except_(ValueError, h)  → ...except_(_poop_ValueError, h)
        ValueError.raise_("boom")        → _poop_ValueError.raise_("boom")
        class MyError(Exception):        → class MyError(_poop_Exception):

    A transformer rather than a `DEFAULT_NAMESPACE` entry: the namespace is
    exactly `Try` and `With`, and every other builtin reaches user code by
    being rewritten to a mangled name. Same shape the Ellipsis transformer
    uses.

    `raise_` needs no ordering constraint any more: it is a class-side message
    on `PoopExcMeta`, so the mirror this rewrites to answers it. The rule that
    `ExceptionTransformer` must run after `RaiseTransformer` existed only
    because that rewrite matched on the name's *spelling*.
    """

    rewriter = _ExceptionRewriter
    BINDINGS = _BINDINGS
