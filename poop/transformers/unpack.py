import ast

from poop.transformers.base import BaseTransformer, rebind


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
        return [node, *(rebind(t, "_poop_list_from") for t in starred)]


class UnpackTransformer(BaseTransformer):
    """Rebinds starred unpacking rest-targets to POOP `List`.

    `_poop_list_from` is provided by the list transformer.
    """

    rewriter = _UnpackRewriter
