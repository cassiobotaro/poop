import ast

from poop.errors import ValidationError
from poop.validators.base import CollectingValidator, collect_errors
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
        # `Ellipsis` is the named spelling of `...`, and EllipsisTransformer
        # rewrites both to `_poop_ellipsis` in every position — so
        # `Ellipsis = 5` did not merely shadow a name, it made the *literal*
        # `...` answer 5 for the rest of the program.
        "Ellipsis",
    }
)

_MESSAGE = "{name!r} is a POOP builtin name; it cannot be rebound"


class NoBuiltinShadowValidator(CollectingValidator):
    def __init__(self) -> None:
        # The exception mirrors belong here for the same reason the names
        # above do: `ExceptionTransformer` rewrites every `ast.Name` matching
        # one, Store included. Both sides of the hazard were live —
        # `ValueError = 5` clobbered the mirror globally, while a parameter or
        # class *name* (neither of which is an `ast.Name`) kept its spelling
        # and left every read of it in the body resolving to the mirror, so
        # `def hold(self, ValueError): return ValueError` answered the class
        # and never saw its argument.
        #
        # Derived from MIRRORS rather than tabulated, as
        # `no_namespace_shadow` derives its own set from DEFAULT_NAMESPACE: a
        # seventeenth mirror must not be addable without the reservation
        # following it. Imported here rather than at module scope for the
        # reason that validator gives — the cycle would close either way, but
        # this keeps the validator -> types edge out of package import time.
        from poop.types.exceptions import MIRRORS

        self._protected: frozenset[str] = _BUILTIN_NAMES | frozenset(MIRRORS)

    def collect(self, tree: ast.Module) -> list[ValidationError]:
        return collect_errors(_Visitor(self._protected, _MESSAGE), tree)
