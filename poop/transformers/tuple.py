import ast
from typing import ClassVar

from poop.types.object import Object
from poop.types.tuple import Tuple


def _poop_tuple(*elements: Object) -> Tuple:
    return Tuple(*elements)


class TupleTransformer:
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_tuple": _poop_tuple}

    def transform(self, tree: ast.Module) -> ast.Module:
        tree = _TupleRewriter().visit(tree)
        ast.fix_missing_locations(tree)
        return tree


class _TupleRewriter(ast.NodeTransformer):
    def visit_Tuple(self, node: ast.Tuple) -> ast.AST:
        self.generic_visit(node)
        if not isinstance(node.ctx, ast.Load):
            return node
        return ast.copy_location(
            ast.Call(
                func=ast.Name(id="_poop_tuple", ctx=ast.Load()),
                args=node.elts,
                keywords=[],
            ),
            node,
        )
