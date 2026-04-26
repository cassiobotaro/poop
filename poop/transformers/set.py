import ast
from poop.transformers.base import BaseTransformer
from collections.abc import Iterable
from typing import ClassVar, cast

from poop.types.object import Object
from poop.types.set import Set


def _poop_set(*elements: Object) -> Set:
    return Set(*elements)


def _poop_set_from(arg: object = None) -> Set:
    from poop.types.interval import Interval

    if arg is None:
        return Set()
    if isinstance(arg, Set):
        return arg
    if isinstance(arg, Interval):
        return Set(*arg._iter())
    if isinstance(arg, Iterable):
        return Set(*cast("Iterable[Object]", arg))
    raise TypeError(f"cannot convert {type(arg).__name__} to Set")

class _SetRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "set"
            and not node.keywords
            and len(node.args) <= 1
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_set_from", ctx=ast.Load()),
                    args=node.args,
                    keywords=[],
                ),
                node,
            )
        return node

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



class SetTransformer(BaseTransformer):
    rewriter = _SetRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_set": _poop_set,
        "_poop_set_from": _poop_set_from,
    }



