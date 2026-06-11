import ast

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
        "enumerate",
        "zip",
    }
)

_MESSAGE = "{name!r} is a POOP builtin name; it cannot be rebound"


class NoBuiltinShadowValidator:
    def validate(self, tree: ast.Module) -> None:
        _Visitor(_BUILTIN_NAMES, _MESSAGE).visit(tree)
