import ast

from poop.transformers.base import BaseTransformer

# Both spellings name POOP's root. `object` is Python's builtin, rewritten
# like every other lowercase one; `Object` is POOP's own name for the same
# class, and is a real name in every position rather than a string the
# `ClassTransformer` recognises only in a base list.
_OBJECT_NAMES = frozenset({"object", "Object"})


class _ObjectRewriter(ast.NodeTransformer):
    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id in _OBJECT_NAMES:
            return ast.copy_location(ast.Name(id="_poop_object", ctx=node.ctx), node)
        return node


class ObjectTransformer(BaseTransformer):
    """Rewrites `object` and `Object` to POOP's root class.

    `ClassTransformer` already rewrites both in a base list, so
    `class Foo(object)` worked while a bare `object` resolved to CPython's
    class and a bare `Object` was a `NameError` — the capital name was
    accepted in exactly one syntactic position, for a name bound nowhere.
    Every other lowercase builtin has had a `Name`-position rewrite all along;
    `object` joined them in proposal 13, and `Object` joins here so the POOP
    spelling resolves everywhere the Python one does.

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
