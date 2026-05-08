import ast
from collections.abc import Iterable
from typing import TYPE_CHECKING, ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.frozen_set import FrozenSet

if TYPE_CHECKING:
    from poop.types.object import Object


def _poop_frozenset_from(iterable: Iterable[Object] | None = None) -> FrozenSet:
    if iterable is not None:
        return FrozenSet(*iterable)
    return FrozenSet()


class _FrozenSetRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "frozenset"
            and not node.keywords
            and len(node.args) <= 1
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_frozenset_from", ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[],
                ),
                node,
            )
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "frozenset":
            return ast.copy_location(ast.Name(id="FrozenSet", ctx=node.ctx), node)
        return node


class FrozenSetTransformer(BaseTransformer):
    rewriter = _FrozenSetRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_frozenset_from": _poop_frozenset_from,
        "FrozenSet": FrozenSet,
    }
