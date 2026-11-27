"""The argument behind `startswith` / `endswith`, on every receiver that has one.

CPython accepts a *tuple* of prefixes, and in POOP that is the only
message-shaped substitute for the forbidden `s.startswith("a") or
s.startswith("b")` — `or` is banned, so there is no other way to ask the
question. Every receiver maps a POOP `Tuple` to a Python one, so the same
program answers the same on `Str`, `Bytes` and `ByteArray`:

    "ab".startswith(("a", "z"))     ->  True
    b"ab".startswith((b"a", b"z"))  ->  True

Passed through raw, the `Tuple` would meet CPython's `startswith first arg
must be bytes or a tuple of bytes, not tuple`: self-contradicting from where
the reader stands, since they *did* pass a tuple — CPython describing its own
`tuple`, which a POOP `Tuple` is not. Only the scalar branch is
string-specific, so the rule lives here rather than in `string.py`.
"""

from poop.types._argument import text_like
from poop.types.tuple import Tuple


def affix_needle[T](
    affix: object, selector: str, expected: str, kinds: tuple[type[T], ...]
) -> T | tuple[T, ...]:
    """The native argument behind a POOP affix, or POOP's refusal.

    A scalar (`Str` / `Bytes` / `ByteArray`) unwraps to its value; a `Tuple` to
    a tuple of its unwrapped members.

    Anything else is `text_like`'s to refuse, in the receiver's own
    `expected`. Reaching CPython raw, it would answer `startswith first arg
    must be str or a tuple of str, not int` — the message as a bare word and
    "arg", the shape `_opt_text` refuses for the strip family — and, for a
    wrong member, `tuple for startswith must only contain str`.
    """
    if isinstance(affix, Tuple):
        return tuple(text_like(p, selector, expected, kinds) for p in affix._items)
    return text_like(affix, selector, expected, kinds)
