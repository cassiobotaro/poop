import ast
from poop.transformers.base import BaseTransformer
from collections.abc import Iterable
from typing import ClassVar, cast

from poop.types.object import Object
from poop.types.tuple import Tuple


def _poop_tuple(*elements: Object) -> Tuple:
    return Tuple(*elements)


def _poop_tuple_from(arg: object = None) -> Tuple:
    from poop.types.range import Range

    if arg is None:
        return Tuple()
    if isinstance(arg, Tuple):
        return arg
    if isinstance(arg, Range):
        return Tuple(*arg._iter())
    if isinstance(arg, Iterable):
        return Tuple(*cast("Iterable[Object]", arg))
    raise TypeError(f"cannot convert {type(arg).__name__} to Tuple")

class _TupleRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "tuple"
            and not node.keywords
            and len(node.args) <= 1
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_tuple_from", ctx=ast.Load()),
                    args=node.args,
                    keywords=[],
                ),
                node,
            )
        return node

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



class TupleTransformer(BaseTransformer):
    rewriter = _TupleRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_tuple": _poop_tuple,
        "_poop_tuple_from": _poop_tuple_from,
    }



