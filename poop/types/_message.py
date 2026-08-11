"""CPython's operator wording, rewritten as message passing.

Every other leak in this family was fixed where the operation lives, because a
wrapper intercepts the call and owns the message. The operator path is the one
that cannot be: `"a" + 1` runs `Str.__add__`, which answers `NotImplemented`,
then `Int.__radd__`, which answers `NotImplemented` too, and only then does
CPython compose a sentence out of the two refusals. No wrapper ever sees the
failure, so there is nothing to catch and nothing to reword at the source.

    "a" + 1        ->  unsupported operand type(s) for +: 'str' and 'int'
    1 < "a"        ->  '<' not supported between instances of 'int' and 'str'
    [1, "a"].sorted()  ->  the same, from inside CPython's sort

`operand type(s)` describes an operator as a type-level protocol rather than a
message, which is the whole distinction POOP exists to make.

**This is the fragile half of the fix and is kept deliberately small.** Matching
another language's message text is a dependency on its internals: Python 3.14
already rewrote the unhashable-key error, and it can rewrite these. Two shapes
are recognised, nothing else, and anything unmatched passes through unchanged —
so a rewording upstream degrades to the old behaviour rather than to a crash.
`tests/test_message.py` pins both shapes against real CPython operations, so an
upgrade that changes them fails loudly instead of silently regressing.
"""

from __future__ import annotations

import re

# A tuple, not the string "aeiou": `"" in "aeiou"` is True, so a nameless type
# answered `an ` — the empty string is a substring of every string.
_VOWELS = ("a", "e", "i", "o", "u")

# `unsupported operand type(s) for +: 'str' and 'int'` — arithmetic and the
# bitwise operators. The selector is whatever CPython names, `+=` included.
_ARITHMETIC = re.compile(
    r"^unsupported operand type\(s\) for (.+?): '(.+?)' and '(.+?)'$"
)

# `'<' not supported between instances of 'int' and 'str'` — the ordering
# comparisons, and what `sorted` / `min` / `max` surface from inside CPython.
_COMPARISON = re.compile(
    r"^'(.+?)' not supported between instances of '(.+?)' and '(.+?)'$"
)


# CPython names some operators by the builtin that also reaches them. POOP has
# no `pow()` or `divmod()` call — both are messages — so the selector is
# normalised back to the spelling a program can actually write.
_SELECTORS = {"** or pow()": "**", "divmod()": "divmod"}


def article(name: str) -> str:
    """`an int`, `a str` — the type name with the article that reads."""
    return f"an {name}" if name[:1].lower() in _VOWELS else f"a {name}"


def no_format_spec(kind: str) -> str:
    """The refusal for a receiver that takes no format spec at all.

    Shared by POOP's two formatting spellings, which is the point: `Object.
    format` composed this from `type(self).__name__` while the template path let
    CPython's `unsupported format string passed to list.__format__` through —
    naming a dunder `no_dunder_attribute` will not let a program spell, from a
    construct the reader wrote with braces.
    """
    return f"{kind} takes no format spec — only a number, a string or bytes does"


def binary_refusal(receiver: str, selector: str, operand: str) -> str:
    """POOP's answer when a receiver will not take that operand for `selector`.

    Deliberately the same shape as `MessageNotUnderstood`'s (`int does not
    understand #plus`), since it is the same kind of refusal: the receiver was
    sent something it does not answer. The operator is kept as the reader typed
    it rather than translated to a verb — POOP allows binary operators, so `+`
    is the spelling in the program.
    """
    return f"{receiver} does not understand #{selector} with {article(operand)}"


def poop_message(exc: BaseException) -> str:
    """`str(exc)`, with the two CPython operator shapes reworded."""
    text = str(exc)
    # Both patterns capture (selector, left, right) in that order, which is
    # why one unpacking serves them.
    match = _ARITHMETIC.match(text) or _COMPARISON.match(text)
    if match is None:
        return text
    selector, receiver, operand = match.groups()
    return binary_refusal(receiver, _SELECTORS.get(selector, selector), operand)
