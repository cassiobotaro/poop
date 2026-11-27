"""The mirrors under their own names.

A call site reads `raise mirrors.TypeError(…)`, not
`raise MIRRORS["TypeError"](…)`: a string key into a module-level dict is how a
registry is read, not how an exception is raised, and its `Literal` key is one
the checker verifies but a reader cannot complete. The mirrors are classes
with fixed names, built once at import, and nothing about them is dynamic
after that — so each is bound here under its own name, once `exceptions` has
built the table.

Every name below *is* POOP's `TypeError`, `ValueError` and so on: the
builtin's name, shadowed on purpose, which is why `A001` is off for this one
module. `MIRRORS` stays for the two readers that are table-shaped —
`poop_class_of`, and the `_at.py` helpers that take a `MirrorName`.
"""

from poop.types.exceptions import MIRRORS

Exception = MIRRORS["Exception"]
ArithmeticError = MIRRORS["ArithmeticError"]
LookupError = MIRRORS["LookupError"]
ZeroDivisionError = MIRRORS["ZeroDivisionError"]
OverflowError = MIRRORS["OverflowError"]
IndexError = MIRRORS["IndexError"]
KeyError = MIRRORS["KeyError"]
AttributeError = MIRRORS["AttributeError"]
NameError = MIRRORS["NameError"]
TypeError = MIRRORS["TypeError"]
ValueError = MIRRORS["ValueError"]
RuntimeError = MIRRORS["RuntimeError"]
NotImplementedError = MIRRORS["NotImplementedError"]
RecursionError = MIRRORS["RecursionError"]
AssertionError = MIRRORS["AssertionError"]
StopIteration = MIRRORS["StopIteration"]
EOFError = MIRRORS["EOFError"]
OSError = MIRRORS["OSError"]
TimeoutError = MIRRORS["TimeoutError"]
CancelledError = MIRRORS["CancelledError"]
