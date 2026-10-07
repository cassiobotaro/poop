import ast
import copy

from poop.transformers.base import BaseTransformer, call_at


def _rebind(target_value: ast.expr) -> ast.Assign:
    """`<t> = _poop_list_from(<t>)` for a starred rest-target `<t>`."""
    store = copy.deepcopy(target_value)  # outermost Store, inner Load
    load = copy.deepcopy(target_value)
    # A starred rest-target is always a single assignable (Name/Attribute;
    # Subscript is rejected by no_subscript) — all of which carry `ctx`.
    if isinstance(load, (ast.Name, ast.Attribute, ast.Subscript, ast.Starred)):
        load.ctx = ast.Load()
    return ast.copy_location(
        ast.Assign(
            targets=[store], value=call_at("_poop_list_from", [load], target_value)
        ),
        target_value,
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
        # A `Starred` in `Store` context is a rest-target, at any depth of the
        # unpacking; a star inside an expression the target reads (a call's
        # `*args` under an attribute) is `Load`, and is left alone.
        starred = [
            star.value
            for target in node.targets
            for star in ast.walk(target)
            if isinstance(star, ast.Starred) and isinstance(star.ctx, ast.Store)
        ]
        if not starred:
            return node
        return [node, *(_rebind(t) for t in starred)]


class UnpackTransformer(BaseTransformer):
    """Rebinds starred unpacking rest-targets to POOP `List`.

    `_poop_list_from` is provided by the list transformer.
    """

    rewriter = _UnpackRewriter
