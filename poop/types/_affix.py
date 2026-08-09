"""The argument behind `startswith` / `endswith`, on every receiver that has one.

CPython accepts a *tuple* of prefixes, and in POOP that is the only
message-shaped substitute for the forbidden `s.startswith("a") or
s.startswith("b")` — `or` is banned, so there is no other way to ask the
question. `Str` mapped a POOP `Tuple` to a Python one; `Bytes` and `ByteArray`
passed their argument through plain `_faithful`, so the same program on the
same data failed:

    "ab".startswith(("a", "z"))     ->  True
    b"ab".startswith((b"a", b"z"))  ->  TypeError: startswith first arg must be
                                        bytes or a tuple of bytes, not tuple

Self-contradicting from where the reader stands: they *did* pass a tuple, and
the sentence told them a tuple is not a tuple — CPython describing its own
`tuple`, which a POOP `Tuple` is not. Only the scalar branch was ever
string-specific, so the rule lives here rather than in `string.py`.
"""

from __future__ import annotations

from typing import Any

from poop.types._unwrap import _faithful


def affix_needle(affix: object) -> Any:
    """The native argument behind a POOP affix, or the affix reaching CPython raw.

    A scalar (`Str` / `Bytes` / `ByteArray`) unwraps to its value; a `Tuple` to
    a tuple of faithfully unwrapped members, so a wrong-typed member reaches
    CPython and raises the faithful error instead of being silently coerced.

    Anything that is neither — an `Int`, a `List` — reaches CPython raw for the
    same reason: reading `._items` off it would answer `int does not understand
    #_items`, naming a POOP internal.
    """
    from poop.types.tuple import Tuple  # circular: tuple imports string

    if isinstance(affix, Tuple):
        return tuple(_faithful(p) for p in affix._items)
    return _faithful(affix)
