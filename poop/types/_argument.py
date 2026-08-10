"""Argument refusals worded as POOP, for the arguments many messages share.

The wrappers reworded the failures they *raise*; the ones CPython raises on
their behalf, about an argument it was handed, were left alone — and those name
the banned builtin as a call (`isinstance() arg 2 must be a type`), or
subscripting and a dunder in one breath (`slice indices must be integers or
None or have an __index__ method`). The mechanical sweep in
`tests/test_no_python_wording.py` found 47 of them across 114 sites, in a
handful of families, which is why the wording lives here rather than being
written out once per receiver.
"""

from __future__ import annotations

from typing import Any

from poop.types._message import article
from poop.types.exceptions import MIRRORS


def a_class(value: Any, selector: str) -> Any:
    """`value` when it can stand for a class, else POOP's refusal.

    `no_isinstance` bans `isinstance(x, T)` and names `x.is_instance(T)`, and
    the substitute's own failure then said `isinstance() arg 2 must be a type,
    a tuple of types, or a union` — the builtin it replaces, spelt as the call
    it replaces. `issubclass` said the same about itself.
    """
    if isinstance(value, type) or isinstance(value, tuple):
        return value
    raise MIRRORS["TypeError"](
        f"#{selector} expects a class, got {article(type(value).__name__)}"
    )


def a_bound(value: Any, selector: str, role: str) -> Any:
    """The raw `start`/`end` behind `value`, or POOP's refusal.

    The `start` / `end` of `find`, `index`, `count`, `startswith` and their
    `r`-prefixed twins are positions, and a wrong one reached CPython's
    sequence machinery: `slice indices must be integers or None or have an
    __index__ method` names subscripting (which `no_subscript` bans) and a
    dunder (which `no_dunder_attribute` bans) in a single sentence, about a
    `slice` the program never wrote. `_resolve_py_slice` guards the real
    `slice` message for the same reason; this is the same guard for the
    messages that carry bounds without one.

    Unwraps as well as guards, so a call site spells one helper where it used
    to spell `_unwrap(start, None)`.
    """
    from poop.types._unwrap import _unwrap

    raw = _unwrap(value, None)
    if raw is None or hasattr(raw, "__index__"):
        return raw
    raise MIRRORS["TypeError"](
        f"#{selector}'s {role} must be an int, got {article(type(value).__name__)}"
    )


def text_like(
    value: Any,
    selector: str,
    expected: str,
    kinds: tuple[type, ...] = (str, bytes, bytearray),
) -> Any:
    """The raw value behind a text argument, or POOP's refusal.

    CPython answers `center() argument 2 must be a byte string of length 1,
    not int` and `replace() argument 1 must be str, not int` — the message
    spelt as a call, every time. `_needle` in `string.py` makes the same move
    for the block case; this covers the rest of the family and the receivers
    that had no guard at all.

    `kinds` narrows what counts as text for the caller that needs it: an
    encoding name and a byte order are `str` and nothing else, so accepting
    `b"utf-8"` here would only move their refusal one line down, into the
    branch that reports a *value* — the split `byte_order` below exists to
    keep straight.
    """
    raw = getattr(value, "_value", value)
    if isinstance(raw, kinds):
        return raw
    raise MIRRORS["TypeError"](
        f"#{selector} expects {expected}, got {article(type(value).__name__)}"
    )


def byte_order(value: Any) -> str:
    """`"big"` / `"little"`, or POOP's refusal.

    `to_bytes` and `from_bytes` handed the argument to CPython, which answered
    `to_bytes() argument 'byteorder' must be str, not int` — the message spelt
    as a call. The two valid spellings are named here rather than left to the
    conversion, so a typo (`"Big"`) is refused by the message that takes it.
    """
    from poop.types._unwrap import _is_absent

    if _is_absent(value):
        return "big"
    # Two failures, two classes, as CPython has them: a non-string is a
    # TypeError about the argument's kind, a misspelt one a ValueError about
    # its value. Only the sentences change.
    raw = text_like(value, "to_bytes", "a str", (str,))
    if raw in ("big", "little"):
        return raw
    raise MIRRORS["ValueError"](f"byte order must be 'big' or 'little', got {raw!r}")


def _opt_stop(bound: Any, end: int) -> int:
    """`bound`, or the whole length when it was absent.

    `list.index` — unlike `str.index` — takes no `None` bound, so a missing
    `stop` becomes the receiver's length. `a_bound` has already unwrapped
    POOP's `none` to Python's `None` by the time this reads it.
    """
    return end if bound is None else bound
