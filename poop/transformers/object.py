import ast
from typing import ClassVar

from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer
from poop.types.object import Object


def _poop_object_from(*args: object, **kwargs: object) -> Object:
    """`object(...)` / `Object(...)`, guarded in call position only.

    The root is bound as the *class*, because `class Foo(Object)` needs a name,
    so a call fell through to CPython: `object(5)` answered `object() takes no
    arguments` — a message spelt as a call, which the wording sweep bans. The
    name position is untouched, which is what keeps the base list working.

    `most=0`: the root really is built from nothing, so both halves of the
    refusal say so. The hint carries no parentheses on purpose — the wording
    sweep's "a message as a call" pattern cannot tell a constructor call from a
    method spelt as one, and a guard with false positives stops being read.
    """
    refuse_extra_arguments(
        "object",
        args,
        kwargs,
        most=0,
        built_from="nothing",
        hint="a bare object is built with no arguments",
    )
    return Object()


# Both spellings name POOP's root. `object` is Python's builtin, rewritten
# like every other lowercase one; `Object` is POOP's own name for the same
# class, and is a real name in every position rather than a string the
# `ClassTransformer` recognises only in a base list.
_OBJECT_NAMES = frozenset({"object", "Object"})


class _ObjectRewriter(ast.NodeTransformer):
    def visit_Call(self, node: ast.Call) -> ast.AST:
        # Call position routes to the factory; every other position falls
        # through to `visit_Name` and stays the class.
        if isinstance(node.func, ast.Name) and node.func.id in _OBJECT_NAMES:
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="_poop_object_from", ctx=ast.Load()),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[
                        ast.keyword(arg=kw.arg, value=self.visit(kw.value))
                        for kw in node.keywords
                    ],
                ),
                node,
            )
        self.generic_visit(node)
        return node

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

    Binds only the call-position factory: `ClassTransformer` already binds
    `_poop_object` for the implicit base, and the namespace build rejects a
    duplicate key rather than letting one transformer quietly overwrite
    another's.

    Order against `ClassTransformer` is genuinely free, unlike
    `ExceptionTransformer`'s against `RaiseTransformer`: whichever runs first
    leaves `_poop_object` behind, which the other no longer matches. It sits
    after so that a base list is already rewritten and this only ever sees the
    spellings `ClassTransformer` does not handle.
    """

    rewriter = _ObjectRewriter
    BINDINGS: ClassVar[dict[str, object]] = {"_poop_object_from": _poop_object_from}
