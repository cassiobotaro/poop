import ast
from collections.abc import Iterable
from typing import TYPE_CHECKING, ClassVar, cast

from poop.transformers.base import BaseTransformer
from poop.types.list import List
from poop.types.range import Range

if TYPE_CHECKING:
    from poop.types.object import Object


def _poop_list(*elements: Object) -> List:
    return List(*elements)


def _poop_list_from(arg: object = None) -> List:
    if arg is None:
        return List()
    if isinstance(arg, List):
        return arg
    if isinstance(arg, Range):
        return List(*arg._iter())
    if isinstance(arg, Iterable):
        return List(*cast("Iterable[Object]", arg))
    raise TypeError(f"cannot convert {type(arg).__qualname__} to List")


class _ListRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "list"
            and not node.keywords
            and len(node.args) <= 1
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_list_from", ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[],
                ),
                node,
            )
        self.generic_visit(node)
        return node

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

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "list":
            return ast.copy_location(ast.Name(id="_poop_list_cls", ctx=node.ctx), node)
        return node


class ListTransformer(BaseTransformer):
    rewriter = _ListRewriter
    BINDINGS: ClassVar[dict[str, object]] = {
        "_poop_list": _poop_list,
        "_poop_list_from": _poop_list_from,
        "_poop_list_cls": List,
    }
