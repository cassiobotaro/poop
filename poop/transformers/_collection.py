"""Shared machinery for the collection transformers.

``list``/``tuple``/``set``/``frozenset``/``dict`` repeat the same
rewriting shape: a ``visit_Call`` routing ``<builtin>(x)`` through a
converter binding, a ``visit_Name`` renaming the bare builtin to its
mangled binding, and (where a literal exists) a visit wrapping the
literal node in the POOP constructor binding.
"""

import ast
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, ClassVar, cast

from poop.types.range import Range

if TYPE_CHECKING:
    from poop.types.object import Object


class CollectionRewriter(ast.NodeTransformer):
    """Rewrites ``<builtin>(x)`` calls and bare ``<builtin>`` names.

    Subclasses set the class vars and add a literal visit when the
    collection has literal syntax.
    """

    builtin: ClassVar[str]
    call_target: ClassVar[str]
    name_target: ClassVar[str]

    def visit_Call(self, node: ast.Call) -> ast.AST:
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == self.builtin
            and not node.keywords
            and len(node.args) <= 1
        ):
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id=self.call_target, ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[],
                ),
                node,
            )
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == self.builtin:
            return ast.copy_location(ast.Name(id=self.name_target, ctx=node.ctx), node)
        return node


def wrap_elts(node: ast.List | ast.Tuple | ast.Set, target: str) -> ast.AST:
    return ast.copy_location(
        ast.Call(
            func=ast.Name(id=target, ctx=ast.Load()),
            args=node.elts,
            keywords=[],
        ),
        node,
    )


def make_constructor[T](poop_type: type[T]) -> Callable[..., T]:
    def _constructor(*elements: Object) -> T:
        return poop_type(*elements)

    return _constructor


def make_iterable_from[T](poop_type: type[T], display_name: str) -> Callable[..., T]:
    def _from(arg: object = None) -> T:
        if arg is None:
            return poop_type()
        if isinstance(arg, poop_type):
            return arg
        if isinstance(arg, Range):
            return poop_type(*arg._iter())
        if isinstance(arg, Iterable):
            return poop_type(*cast("Iterable[Object]", arg))
        raise TypeError(f"cannot convert {type(arg).__qualname__} to {display_name}")

    return _from
