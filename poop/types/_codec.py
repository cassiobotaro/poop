"""What `encode` and `decode` accept, checked before CPython's codec table.

`Str.encode` handed the codec name straight to CPython, whose failure advertised
a module POOP does not have and could not import:

    "a".encode("rot13")
      ->  LookupError: 'rot13' is not a text encoding; use codecs.encode()
          to handle arbitrary codecs

The advice is unfollowable — `import` is forbidden and `_ALLOWED_BUILTINS` has
no route to a module — so the message sent the reader somewhere POOP cannot go.
`poop/types/exceptions.py` argues in its own docstring that "a language with no
I/O and no codecs cannot reach the `OSError` subtree or the `Unicode*` family";
the codec *table* was still reachable through this one argument.

So the surface is named rather than inherited. Four text encodings and the
three codec-independent error handlers — `backslashreplace`, `namereplace` and
`surrogateescape` are the same machinery reached by another name.
"""

from __future__ import annotations

from typing import Any

from poop.types._argument import text_like
from poop.types.exceptions import MIRRORS

# Canonical spelling -> what a program may write for it. CPython normalises far
# more aggressively (`UTF_8`, `u8`); POOP takes the spellings a reader would
# reasonably type and refuses the rest, so the accepted set stays readable.
_ENCODINGS: dict[str, frozenset[str]] = {
    "utf-8": frozenset({"utf-8", "utf8"}),
    "utf-16": frozenset({"utf-16", "utf16"}),
    "latin-1": frozenset({"latin-1", "latin1", "iso-8859-1"}),
    "ascii": frozenset({"ascii", "us-ascii"}),
}

_HANDLERS = ("strict", "ignore", "replace")


def _listed(names: tuple[str, ...] | list[str]) -> str:
    return f"{', '.join(names[:-1])} and {names[-1]}"


def encoding_name(name: Any, selector: str) -> str:
    """The canonical name behind `name`, or a POOP refusal.

    Guarded before the lookup, not after: the table is read by lowercasing the
    argument, so a non-text one answered `'int' object has no attribute
    'lower'` — the wrapper naming the Python method it happens to call, which
    is the leak `_argument.py` exists to close everywhere else. `selector` is
    the message the reader sent (`encode` or `decode`), so the refusal names
    the spelling in the program rather than this shared helper.
    """
    # The guarded raw text carries the refusal, not the argument as handed in:
    # a `Str` reaching here directly would otherwise print through its own
    # repr, and the two spellings of the same mistake must read alike.
    raw = text_like(name, selector, "a str", (str,))
    wanted = raw.lower().replace("_", "-")
    for canonical, spellings in _ENCODINGS.items():
        if wanted in spellings:
            return canonical
    raise MIRRORS["ValueError"](
        f"unknown encoding {raw!r} — POOP encodes {_listed(list(_ENCODINGS))}"
    )


def handler_name(name: Any, selector: str) -> str:
    """The error handler behind `name`, or a POOP refusal.

    Checked for the same reason as the encoding: `namereplace` and
    `backslashreplace` are the codec machinery under another argument.

    Two failures, two classes, as `byte_order` has them: a non-string is a
    `TypeError` about the argument's kind, a misspelt one a `ValueError` about
    its value. Without the first, `"a".encode("utf-8", 1)` reported an
    *unknown handler* named `1`, describing a wrong-typed argument as a
    wrong-valued one.
    """
    raw = text_like(name, selector, "a str", (str,))
    if raw in _HANDLERS:
        return raw
    raise MIRRORS["ValueError"](
        f"unknown error handler {raw!r} — POOP handles {_listed(_HANDLERS)}"
    )


def _refusal(exc: UnicodeError, encoding: str, verb: str) -> Exception:
    """POOP's sentence for text the named encoding cannot carry.

    CPython answers `'ascii' codec can't encode character '\\xe9' in position
    1: ordinal not in range(128)`, under a class no POOP program can spell
    (`UnicodeEncodeError`). Both halves are the surface this module exists to
    close: `codec` sends the reader to a module POOP cannot import, and the
    class is outside the mirrored hierarchy, so a handler was told the kind
    was `ValueError` while the uncaught report printed `UnicodeEncodeError` —
    one failure under two names.

    A `ValueError`, which is what `UnicodeError` is in CPython's tree too, so
    `except_(ValueError, …)` catches exactly what it caught before.
    """
    start = getattr(exc, "start", 0)
    subject = getattr(exc, "object", "")[start : start + 1]
    shown = f"byte 0x{subject[0]:02x}" if isinstance(subject, bytes) else repr(subject)
    return MIRRORS["ValueError"](
        f"{encoding} cannot {verb} {shown} at position {start}"
    )


def encoded(text: str, encoding: Any, errors: Any) -> bytes:
    """`text` as bytes, with both arguments and the failure worded by POOP."""
    name = encoding_name(encoding, "encode")
    try:
        return text.encode(name, handler_name(errors, "encode"))
    except UnicodeEncodeError as exc:
        raise _refusal(exc, name, "encode") from None


def decoded(data: bytes | bytearray, encoding: Any, errors: Any) -> str:
    """`data` as text, with both arguments and the failure worded by POOP."""
    name = encoding_name(encoding, "decode")
    try:
        return data.decode(name, handler_name(errors, "decode"))
    except UnicodeDecodeError as exc:
        raise _refusal(exc, name, "decode") from None
