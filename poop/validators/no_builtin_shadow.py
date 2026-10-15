from poop.transformers import RESERVED_NAMES
from poop.validators._shadow import ShadowValidator

# The names the type transformers rewrite to mangled `_poop_*` globals.
# Rebinding one (an assignment, a class name, or a def/lambda parameter)
# silently retargets the interpreter's internals — e.g. `str = "x"` replaces
# the literal constructor, and `def m(self, dict)` makes the body operate on
# the internal Dict class instead of the argument. Reserving them turns the
# silent corruption into a parse-time diagnostic, mirroring how
# `no_namespace_shadow` protects namespace bindings.
#
# Three spellings are easy to miss. `object` and `Object` both rewrite to
# `_poop_object` in every position, so `object = 5` clobbers the root class
# itself and the next `class Foo` implicitly inherits an Int. `Ellipsis` is
# the named spelling of `...`, so `Ellipsis = 5` made the *literal* `...`
# answer 5 for the rest of the program. The exception mirrors are rewritten
# the same way, so `ValueError = 5` clobbered the mirror globally.
#
# Derived from the rewriters (`RESERVED_NAMES`), not tabulated here: a table
# is a second list, and a new rewriter must not be addable without its
# reservation following it.


class NoBuiltinShadowValidator(ShadowValidator):
    protected = RESERVED_NAMES
    message = "{name!r} is a POOP builtin name; it cannot be rebound"
