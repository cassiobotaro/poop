import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer, name_at
from poop.types.exceptions import MIRRORS

_BINDINGS: dict[str, object] = {
    f"_poop_{name}": mirror for name, mirror in MIRRORS.items()
}


class _ExceptionRewriter(ast.NodeTransformer):
    # Every mirror name, rewritten in every position, Store included — so
    # `RESERVED_NAMES` derives the reservation from here, as it does from the
    # `BuiltinRewriter`s and `_EllipsisRewriter`. Unreserved, the hazard cuts
    # both ways: `ValueError = 5` would clobber the mirror globally, while a
    # parameter or class *name* (neither an `ast.Name`) keeps its spelling and
    # leaves every read in the body resolving to the mirror, so `def
    # hold(self, ValueError): return ValueError` would answer the class and
    # never see its argument.
    names: ClassVar[frozenset[str]] = frozenset(MIRRORS)

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id in self.names:
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

    `raise_` puts no ordering constraint on this transformer: it is a
    class-side message on `PoopExcMeta`, so the mirror this rewrites to
    answers it.
    """

    rewriter = _ExceptionRewriter
    BINDINGS = _BINDINGS
