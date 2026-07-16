import ast

from poop.transformers.base import BaseTransformer


class _ObjectRewriter(ast.NodeTransformer):
    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id == "object":
            return ast.copy_location(ast.Name(id="_poop_object", ctx=node.ctx), node)
        return node


class ObjectTransformer(BaseTransformer):
    """Rewrites `object` to POOP's root class.

    `ClassTransformer` already rewrites `object` in a base list, so
    `class Foo(object)` worked while a bare `object` resolved to CPython's
    class — `object.class_name()` answered `type object 'object' has no
    attribute 'class_name'`, making "no naked Python primitive ever reaches
    runtime" false about the root class itself. Every other lowercase builtin
    has had a `Name`-position rewrite all along.

    Declares no BINDINGS: `ClassTransformer` already binds `_poop_object` for
    the implicit base, and the namespace build rejects a duplicate key rather
    than letting one transformer quietly overwrite another's.

    Order against `ClassTransformer` is genuinely free, unlike
    `ExceptionTransformer`'s against `RaiseTransformer`: whichever runs first
    leaves `_poop_object` behind, which the other no longer matches. It sits
    after so that a base list is already rewritten and this only ever sees the
    spellings `ClassTransformer` does not handle.
    """

    rewriter = _ObjectRewriter
