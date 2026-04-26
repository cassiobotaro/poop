import ast
from typing import ClassVar

from poop.transformers.base import BaseTransformer
from poop.types.object import Object


class _ClassRewriter(ast.NodeTransformer):
    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        self.generic_visit(node)

        object_base = ast.Name(id="Object", ctx=ast.Load())

        if not node.bases:
            node.bases = [object_base]
            return node

        new_bases = []
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "object":
                new_bases.append(object_base)
            else:
                new_bases.append(base)
        node.bases = new_bases
        return node


class ClassTransformer(BaseTransformer):
    """Implicitly injects Object as base class when none is specified.

    Rewrites:
        class Foo:         → class Foo(Object):
        class Foo(object): → class Foo(Object):
        class Foo(Bar):    → unchanged (already has a POOP or custom base)

    This mirrors Python 3's implicit inheritance from `object`, but uses
    POOP's Object so user classes gain print(), responds_to(), is_nil(), etc.
    """

    rewriter = _ClassRewriter
    BINDINGS: ClassVar[dict[str, object]] = {"Object": Object}
