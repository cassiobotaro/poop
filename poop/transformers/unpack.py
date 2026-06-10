import ast
import copy
from typing import ClassVar

from poop.transformers.base import BaseTransformer


def _collect_starred(target: ast.expr, acc: list[ast.expr]) -> None:
    if isinstance(target, ast.Starred):
        acc.append(target.value)
    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            _collect_starred(elt, acc)


def _rebind(target_value: ast.expr) -> ast.Assign:
    """`<t> = _poop_list_from(<t>)` for a starred rest-target `<t>`."""
    store = copy.deepcopy(target_value)  # outermost Store, inner Load
    load = copy.deepcopy(target_value)
    # A starred rest-target is always a single assignable (Name/Attribute;
    # Subscript is rejected by no_subscript) — all of which carry `ctx`.
    if isinstance(load, (ast.Name, ast.Attribute, ast.Subscript, ast.Starred)):
        load.ctx = ast.Load()
    return ast.Assign(
        targets=[store],
        value=ast.Call(
            func=ast.Name(id="_poop_list_from", ctx=ast.Load()),
            args=[load],
            keywords=[],
        ),
    )


class _UnpackRewriter(ast.NodeTransformer):
    """Re-wrap a starred unpacking rest-target as a POOP `List`.

    CPython's `UNPACK_EX` builds the rest-collection of `c, *rest = xs` as
    a raw `builtins.list` (its elements are POOP values, the container is
    not), so every POOP message on it crashes. After each assignment that
    contains a `*target`, append `target = _poop_list_from(target)` — one
    per starred name, handling nested (`a, (b, *inner) = …`) and attribute
    (`a, *self.rest = …`) targets.
    """

    def visit_Assign(self, node: ast.Assign) -> ast.AST | list[ast.stmt]:
        self.generic_visit(node)
        starred: list[ast.expr] = []
        for target in node.targets:
            _collect_starred(target, starred)
        if not starred:
            return node
        return [node, *(_rebind(t) for t in starred)]


class UnpackTransformer(BaseTransformer):
    """Rebinds starred unpacking rest-targets to POOP `List`.

    `_poop_list_from` is provided by the list transformer.
    """

    rewriter = _UnpackRewriter
    BINDINGS: ClassVar[dict[str, object]] = {}
