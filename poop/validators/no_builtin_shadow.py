from poop.transformers import RESERVED_NAMES
from poop.types.exceptions import MIRRORS
from poop.validators._shadow import ShadowValidator

# The names the type transformers rewrite to mangled `_poop_*` globals.
# Rebinding one (an assignment, a class name, or a def/lambda parameter)
# silently retargets the interpreter's internals — e.g. `str = "x"` replaces
# the literal constructor, and `def m(self, dict)` makes the body operate on
# the internal Dict class instead of the argument. Reserving them turns the
# silent corruption into a parse-time diagnostic, mirroring how
# `no_namespace_shadow` protects namespace bindings.
#
# Two spellings are easy to miss. `object` and `Object` both rewrite to
# `_poop_object` in every position, so `object = 5` clobbers the root class
# itself and the next `class Foo` implicitly inherits an Int. `Ellipsis` is
# the named spelling of `...`, so `Ellipsis = 5` made the *literal* `...`
# answer 5 for the rest of the program.
#
# Derived from the rewriters (`RESERVED_NAMES`), not tabulated here: a table
# is a second list, and a new rewriter must not be addable without its
# reservation following it.


class NoBuiltinShadowValidator(ShadowValidator):
    # The exception mirrors belong here for the same reason the names above
    # do: `ExceptionTransformer` rewrites every `ast.Name` matching one, Store
    # included. Both sides of the hazard were live — `ValueError = 5`
    # clobbered the mirror globally, while a parameter or class *name*
    # (neither of which is an `ast.Name`) kept its spelling and left every
    # read of it in the body resolving to the mirror, so `def hold(self,
    # ValueError): return ValueError` answered the class and never saw its
    # argument.
    #
    # Derived from MIRRORS rather than tabulated, for the reason the
    # rewriters' names are: a new mirror must not be addable without the
    # reservation following it.
    protected = RESERVED_NAMES | frozenset(MIRRORS)
    message = "{name!r} is a POOP builtin name; it cannot be rebound"
