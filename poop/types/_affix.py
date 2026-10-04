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

from typing import Any

from poop.types._argument import text_like
from poop.types.tuple import Tuple


def affix_needle(
    affix: object, selector: str, expected: str, kinds: tuple[type, ...]
) -> Any:
    """The native argument behind a POOP affix, or POOP's refusal.

    A scalar (`Str` / `Bytes` / `ByteArray`) unwraps to its value; a `Tuple` to
    a tuple of its unwrapped members.

    Anything else used to reach CPython raw, which answered `startswith first
    arg must be str or a tuple of str, not int` — the message as a bare word
    and "arg", the shape `_opt_text` replaced for the strip family — and, for a
    wrong member, `tuple for startswith must only contain str`. Both are
    `text_like`'s to refuse, in the receiver's own `expected`.
    """
    if isinstance(affix, Tuple):
        return tuple(text_like(p, selector, expected, kinds) for p in affix._items)
    return text_like(affix, selector, expected, kinds)
