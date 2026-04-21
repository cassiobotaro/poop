import ast
from typing import ClassVar

from poop.types.list import List
from poop.types.object import Object


def _poop_list(*elements: Object) -> List:
    return List(*elements)


class ListTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_list": _poop_list}

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _ListRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _ListRewriter(ast.NodeTransformer):
    def visit_List(self, node: ast.List) -> ast.AST:
        self.generic_visit(node)
        if not isinstance(node.ctx, ast.Load):
            return node
        return ast.copy_location(
            ast.Call(
                func=ast.Name(id="_poop_list", ctx=ast.Load()),
                args=node.elts,
                keywords=[],
            ),
            node,
        )
