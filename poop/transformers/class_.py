import ast

from poop.transformers.base import BaseTransformer, name_at
from poop.types.object import Object


class _ClassRewriter(ast.NodeTransformer):
    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        self.generic_visit(node)
        # Only the implicit base is this rewriter's: an explicit `object` or
        # `Object` in a base list is rewritten by `ObjectTransformer`, which
        # handles both spellings in every position.
        if not node.bases:
            node.bases = [name_at("_poop_object", node)]
        return node


class ClassTransformer(BaseTransformer):
    """Implicitly injects Object as base class when none is specified.

    Rewrites:
        class Foo:         → class Foo(Object):
        class Foo(Bar):    → unchanged (already has a POOP or custom base)

    `class Foo(object)` is `ObjectTransformer`'s, which rewrites the name
    wherever it appears.

    This mirrors Python 3's implicit inheritance from `object`, but uses
    POOP's Object so user classes gain print(), is_none(), not_none(),
    class_name(), is_instance(), etc.
    """

    rewriter = _ClassRewriter
    BINDINGS = {"_poop_object": Object}
