"""The shared refusal for a constructor call the converter cannot take.

Every `<builtin>(...)` reaches its converter whatever its arity, and the
converter refuses in POOP's vocabulary. A rewriter that guarded `visit_Call` on
the arity it can handle (`not node.keywords and len(node.args) <= 1`) and let
anything else fall through to `visit_Name` would send the call to the *class*
binding. The class constructor is variadic — `List(*elements)` — so one name
would mean "convert" at one arity and "build from these elements" at another:
`list(1, 2)` would build a list where CPython answers `list expected at most 1
argument`. `list(a, b)` is a plausible slip for `[a, b]`, and CPython exists to
catch it. A scalar wrapper reached that way would report a bad call against
`__init__` — a dunder `no_dunder_attribute` bans outright — from a construct
the program spelled without a dunder anywhere.

Three constructors need more than the arity: `object` takes no argument at all,
`zip` legitimately takes any number of iterables so only its `strict` keyword
is real, and `slice` needs a factory in front of the class, whose refusal would
name `__init__` too.
"""

from typing import TYPE_CHECKING

from poop.types import mirrors

if TYPE_CHECKING:
    from collections.abc import Mapping


def refuse_extra_arguments(  # noqa: PLR0913 — one sentence, every part of it named
    name: str,
    args: tuple[object, ...],
    kwargs: Mapping[str, object],
    *,
    most: int,
    built_from: str,
    hint: str,
    empty: bool = True,
    keywords: bool = False,
) -> None:
    """Refuse a call the builtin itself would refuse, in POOP's words.

    `built_from` reads into both sentences (`dict is built from one mapping`),
    and `hint` points at the spelling that works. `empty=False` marks
    the constructors that cannot be called with nothing (`range()`); `keywords`
    marks the one constructor that legitimately takes them — `dict(a=1)`.
    """
    if kwargs and not keywords:
        raise mirrors.TypeError(
            f"{name} takes no keyword arguments — it is built from {built_from}"
        )
    if len(args) > most:
        # Pluralised for `object`'s `most=0`, the one limit a single argument
        # is over: without it the refusal would read `got 1 arguments`.
        given = f"{len(args)} argument" + ("" if len(args) == 1 else "s")
        raise mirrors.TypeError(
            f"{name} is built from {built_from}, got {given} — {hint}"
        )
    if not args and not empty:
        raise mirrors.TypeError(
            f"{name} is built from {built_from}, got nothing — {hint}"
        )
