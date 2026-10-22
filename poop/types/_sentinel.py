"""Markers for "nothing here" where `None` cannot say it.

POOP's `none` is a value a program passes, stores and yields, so neither it nor
Python's `None` can stand for "the caller passed nothing" or "this operand is
not a number". Each of those used to be its own `object()` typed `Any`: seven
of them, three meaning the same thing — "argument not given" — and imported
side by side into `_iterable_mixin`, so which one a parameter defaulted to
depended on which helper its author had been reading.

Python 3.15's `sentinel` (PEP 661) instead, one per marker: identity still
drives every test (`x is MISSING`), the repr is the name, and the marker *is*
its own type in an annotation — `block: Block | MISSING = MISSING` — which a
type checker narrows on `is`, so the branch after `if x is MISSING` sees the
other operand. The markers were an `Enum` built to imitate exactly that, with
a `Literal[...]` alias per member for the annotations; the builtin gives all
three properties natively, and the aliases went with the enum.

Declared bare, without `Final`: a `Final` annotation hides the sentinel's type
from the checker, and the union stops narrowing. The module's leading
underscore is the guard against rebinding, as it was for the enum.
"""

# An argument the caller did not pass: the block slot of `do` / `map` /
# `reduce`, the `default` of `min` / `max` / `next`, the `start` of `sum`.
MISSING = sentinel("MISSING")
# Nothing buffered by `has_next` — distinct from a buffered `none`, which an
# iterator yielding POOP's `none` must be able to park.
UNPEEKED = sentinel("UNPEEKED")
# An operand that is no repeat count, so `*` answers `NotImplemented`.
NOT_A_COUNT = sentinel("NOT_A_COUNT")
# An operand outside the numeric tower, for the comparisons and arithmetic.
NOT_NUMERIC = sentinel("NOT_NUMERIC")
# An operand the bitwise and shift operators cannot take.
NOT_INTEGRAL = sentinel("NOT_INTEGRAL")
