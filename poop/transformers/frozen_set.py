import ast
from collections.abc import Iterable
from typing import ClassVar

from poop.types.frozen_set import FrozenSet
from poop.types.object import Object


def _poop_frozenset_from(iterable: Iterable[Object] | None = None) -> FrozenSet:
    if iterable is not None:
        return FrozenSet(*iterable)
    return FrozenSet()


class FrozenSetTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_frozenset_from": _poop_frozenset_from
    }

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _FrozenSetRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _FrozenSetRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "frozenset"
            and not node.keywords
            and len(node.args) <= 1
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_frozenset_from", ctx=ast.Load()),
                    args=node.args,
                    keywords=[],
                ),
                node,
            )
        return node
