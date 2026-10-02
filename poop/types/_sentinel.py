"""Markers for "nothing here" where `None` cannot say it.

POOP's `none` is a value a program passes, stores and yields, so neither it nor
Python's `None` can stand for "the caller passed nothing" or "this operand is
not a number". Each of those used to be its own `object()` typed `Any`: seven
of them, three meaning the same thing — "argument not given" — and imported
side by side into `_iterable_mixin`, so which one a parameter defaulted to
depended on which helper its author had been reading.

Members of one `Enum` instead: identity still drives every test (`x is
MISSING`), a type checker narrows on it, and the repr names the marker rather
than printing an address.
"""

from enum import Enum, auto
from typing import Final, Literal


class Sentinel(Enum):
    # An argument the caller did not pass: the block slot of `do` / `map` /
    # `reduce`, the `default` of `min` / `max` / `next`, the `start` of `sum`.
    MISSING = auto()
    # Nothing buffered by `has_next` — distinct from a buffered `none`, which an
    # iterator yielding POOP's `none` must be able to park.
    UNPEEKED = auto()
    # An operand that is no repeat count, so `*` answers `NotImplemented`.
    NOT_A_COUNT = auto()
    # An operand outside the numeric tower, for the comparisons and arithmetic.
    NOT_NUMERIC = auto()
    # An operand the bitwise and shift operators cannot take.
    NOT_INTEGRAL = auto()

    def __repr__(self) -> str:
        return f"<{self.name.lower()}>"


MISSING: Final = Sentinel.MISSING
UNPEEKED: Final = Sentinel.UNPEEKED
NOT_A_COUNT: Final = Sentinel.NOT_A_COUNT
NOT_NUMERIC: Final = Sentinel.NOT_NUMERIC
NOT_INTEGRAL: Final = Sentinel.NOT_INTEGRAL

# The type of a parameter that may be left out: `block: Block | Missing = MISSING`.
type Missing = Literal[Sentinel.MISSING]
