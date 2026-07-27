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


def encoding_name(name: str) -> str:
    """The canonical name behind `name`, or a POOP refusal."""
    wanted = name.lower().replace("_", "-")
    for canonical, spellings in _ENCODINGS.items():
        if wanted in spellings:
            return canonical
    raise MIRRORS["ValueError"](
        f"unknown encoding {name!r} — POOP encodes {_listed(list(_ENCODINGS))}"
    )


def handler_name(name: str) -> str:
    """The error handler behind `name`, or a POOP refusal.

    Checked for the same reason as the encoding: `namereplace` and
    `backslashreplace` are the codec machinery under another argument.
    """
    if name in _HANDLERS:
        return name
    raise MIRRORS["ValueError"](
        f"unknown error handler {name!r} — POOP handles {_listed(_HANDLERS)}"
    )
