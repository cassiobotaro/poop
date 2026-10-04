from poop.transformers._arity import refuse_extra_arguments
from poop.transformers.base import BaseTransformer, BuiltinRewriter
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


class _ObjectRewriter(BuiltinRewriter):
    # Call position routes to the factory; every other position stays the class.
    call_target = "_poop_object_from"
    name_target = "_poop_object"

    def is_builtin(self, name: str) -> bool:
        return name in _OBJECT_NAMES


class ObjectTransformer(BaseTransformer):
    """Rewrites `object` and `Object` to POOP's root class.

    `ClassTransformer` used to rewrite both in a base list, so
    `class Foo(object)` worked while a bare `object` resolved to CPython's
    class and a bare `Object` was a `NameError` — the capital name was
    accepted in exactly one syntactic position, for a name bound nowhere.
    Every other lowercase builtin has had a `Name`-position rewrite all along;
    `object` joined them first, and `Object` joins here so the POOP spelling
    resolves everywhere the Python one does.

    Binds only the call-position factory: `ClassTransformer` already binds
    `_poop_object` for the implicit base, and the namespace build rejects a
    duplicate key rather than letting one transformer quietly overwrite
    another's.

    Order against `ClassTransformer` is free: that one only adds the implicit
    base to a class with none, and every spelt `object` or `Object` — a base
    list included — is this rewriter's.
    """

    rewriter = _ObjectRewriter
    BINDINGS = {"_poop_object_from": _poop_object_from}
