import ast
from collections.abc import Iterable
from typing import TYPE_CHECKING, ClassVar, cast

from poop.transformers.base import BaseTransformer
from poop.types.range import Range
from poop.types.set import Set

if TYPE_CHECKING:
    from poop.types.object import Object


def _poop_set(*elements: Object) -> Set:
    return Set(*elements)


def _poop_set_from(arg: object = None) -> Set:
    if arg is None:
        return Set()
    if isinstance(arg, Set):
        return arg
    if isinstance(arg, Range):
        return Set(*arg._iter())
    if isinstance(arg, Iterable):
        return Set(*cast("Iterable[Object]", arg))
    raise TypeError(f"cannot convert {type(arg).__qualname__} to Set")


class _SetRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "set"
            and not node.keywords
            and len(node.args) <= 1
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_set_from", ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[],
                ),
                node,
            )
        self.generic_visit(node)
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

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "set":
            return ast.copy_location(ast.Name(id="_poop_set_cls", ctx=node.ctx), node)
        return node


class SetTransformer(BaseTransformer):
    rewriter = _SetRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_set": _poop_set,
        "_poop_set_from": _poop_set_from,
        "_poop_set_cls": Set,
    }
