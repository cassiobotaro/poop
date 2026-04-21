import ast
from typing import ClassVar

from poop.types.object import Object
from poop.types.set import Set


def _poop_set(*elements: Object) -> Set:
    return Set(*elements)


class SetTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_set": _poop_set}

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _SetRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _SetRewriter(ast.NodeTransformer):
    def visit_Set(self, node: ast.Set) -> ast.AST:
        self.generic_visit(node)
        return ast.copy_location(
            ast.Call(
                func=ast.Name(id="_poop_set", ctx=ast.Load()),
                args=node.elts,
                keywords=[],
            ),
            node,
        )
