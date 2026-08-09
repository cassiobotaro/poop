"""The shared refusal for a constructor call the converter cannot take.

Every builtin-constructor rewriter used to guard its `visit_Call` on the arity
it could handle (`not node.keywords and len(node.args) <= 1`) and let anything
else fall through to `visit_Name`, which renames the bare builtin to the
*class* binding. The class constructor is variadic — `List(*elements)` — so
one name meant "convert" at one arity and "build from these elements" at
another, and only the first matches Python:

    list(1, 2).print()   ->  1 2      CPython: list expected at most 1 argument
    set(1, 2).print()    ->  {1, 2}   CPython: set expected at most 1 argument

`list(a, b)` is a plausible slip for `[a, b]`, and CPython exists to catch it.
The scalar wrappers fell through the same way, and there the answer was right
but the report named `__init__` — a dunder `no_dunder_attribute` bans outright
— from a construct the program spelled without a dunder anywhere:

    str(b"ab", "utf-8")  ->  str.__init__() takes 2 positional arguments but 3 …

So the call path is complete now: every `<builtin>(...)` reaches the converter
whatever its arity, and the converter refuses in POOP's vocabulary.
"""

from collections.abc import Mapping

from poop.types.exceptions import MIRRORS


def refuse_extra_arguments(
    name: str,
    args: tuple[object, ...],
    kwargs: Mapping[str, object],
    *,
    most: int,
    built_from: str,
    hint: str,
    keywords: bool = False,
) -> None:
    """Refuse a call the builtin itself would refuse, in POOP's words.

    `built_from` reads into both sentences (`dict is built from one mapping`),
    and `hint` points at the spelling that works. `keywords` marks the one
    constructor that legitimately takes them — `dict(a=1)`.
    """
    if kwargs and not keywords:
        raise MIRRORS["TypeError"](
            f"{name} takes no keyword arguments — it is built from {built_from}"
        )
    if len(args) > most:
        raise MIRRORS["TypeError"](
            f"{name} is built from {built_from}, got {len(args)} arguments — {hint}"
        )
