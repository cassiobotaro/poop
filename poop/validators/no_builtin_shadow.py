import ast

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator
from poop.validators.no_namespace_shadow import _Visitor

# The lowercase builtin names the type transformers rewrite to mangled
# `_poop_*` globals. Rebinding one (an assignment, a class name, or a
# def/lambda parameter) silently retargets the interpreter's internals —
# e.g. `str = "x"` replaces the literal constructor, and `def m(self, dict)`
# makes the body operate on the internal Dict class instead of the argument.
# Reserving them turns the silent corruption into a parse-time diagnostic,
# mirroring how `no_namespace_shadow` protects namespace bindings.
_BUILTIN_NAMES = frozenset(
    {
        # `object` and `Object` are the two spellings ObjectTransformer
        # rewrites to `_poop_object` in every position, Store included. So
        # `object = 5` becomes `_poop_object = 5` and clobbers the root class
        # itself — the next `class Foo` then implicitly inherits an Int. A
        # method parameter named `object` is the same hazard as one named
        # `dict`: the body's references rewrite to the class, not the argument.
        "object",
        "Object",
        "bool",
        "int",
        "float",
        "complex",
        "str",
        "bytes",
        "bytearray",
        "memoryview",
        "list",
        "tuple",
        "dict",
        "set",
        "frozenset",
        "range",
        "slice",
        "enumerate",
        "zip",
    }
)

_MESSAGE = "{name!r} is a POOP builtin name; it cannot be rebound"


class NoBuiltinShadowValidator(CollectingValidator):
    def collect(self, tree: ast.Module) -> list[ValidationError]:
        visitor = _Visitor(_BUILTIN_NAMES, _MESSAGE)
        visitor.visit(tree)
        return visitor.errors
