"""POOP's exception hierarchy — the class side of `Try` and `raise_`.

`Try.except_(ValueError, handler)` and `ValueError.raise_("msg")` used to take a
native CPython class, the last raw primitive in POOP's own substitutes for two
forbidden constructs. `INFECTIONS.md` justified it with "mirroring Python's full
hierarchy (~100+ classes) is impractical"; Python 3.14 has 71 builtin
exceptions, and a language with no I/O and no codecs cannot reach the `OSError`
subtree or the `Unicode*` family. What it can reach is the table below.

No translation layer is needed, which is what makes this cheap: `Try._execute()`
catches `except BaseException` and then matches with `isinstance()` — POOP's own
code, never a Python `except` clause — so a metaclass `__instancecheck__` is
enough for a POOP class to match its native twin. The mirrors subclass that twin
so they stay raisable, which is what `raise_` depends on.

`MIRRORS` is also how POOP raises its *own* diagnostics. A wrapper composing a
POOP message used to carry it on a native class — POOP's advice labelled with
Python's vocabulary — and nothing stopped the next one from doing the same. The
rule is now one line: inside `poop/types/` and `poop/transformers/`, a failure a
program can reach is raised as `MIRRORS[...]`, never as the bare builtin.
Subclassing keeps it catchable by anything that caught the native, so the rule
costs nothing; `tests/test_mirrored_raises.py` sweeps both packages for it.
"""

from __future__ import annotations

from typing import Any, cast

from poop.types.meta import PoopMeta
from poop.types.object import Object


class PoopExcMeta(PoopMeta):
    """Matches a POOP exception class against the native one it mirrors."""

    def __instancecheck__(cls, obj: object) -> bool:
        # `_native` is read from the class's own __dict__, never inherited: a
        # user's `class MyError(Exception)` would otherwise inherit the root's
        # `_native = Exception` and catch every exception in the program —
        # silent and total. Falling back to normal behaviour makes a user
        # subclass match itself. The obvious alternative, an __init_subclass__
        # setting `_native = cls`, recurses forever: __instancecheck__ would
        # call itself.
        native = cls.__dict__.get("_native")
        if native is None:
            return super().__instancecheck__(obj)
        return isinstance(obj, native)


# (native class, the POOP parent's name) — mirrors Python's own tree, so
# `except_(LookupError, ...)` catches a raw KeyError the way `except` does.
_HIERARCHY: tuple[tuple[type[BaseException], str | None], ...] = (
    (Exception, None),
    (ArithmeticError, "Exception"),
    (LookupError, "Exception"),
    (ZeroDivisionError, "ArithmeticError"),
    (OverflowError, "ArithmeticError"),
    (IndexError, "LookupError"),
    (KeyError, "LookupError"),
    (AttributeError, "Exception"),
    (NameError, "Exception"),
    (TypeError, "Exception"),
    (ValueError, "Exception"),
    (RuntimeError, "Exception"),
    (NotImplementedError, "RuntimeError"),
    # Recursion is POOP's substitute for every loop, so this is the most
    # reachable of the lot rather than an exotic one.
    (RecursionError, "RuntimeError"),
    (AssertionError, "Exception"),
    (StopIteration, "Exception"),
)

# Annotated as exception classes, not bare `type`: every POOP diagnostic is
# raised through this table (`raise MIRRORS["TypeError"](...)`), so the values
# have to be raisable to the type checker as well as at runtime.
MIRRORS: dict[str, type[Exception]] = {}
NATIVE_TO_POOP: dict[type[BaseException], type] = {}


def _build(native: type[BaseException], parent: str | None) -> None:
    # The root also inherits Object, so a user's `class MyError(Exception)`
    # lands inside the Object tree and answers print()/class_name() — before
    # this it sat outside it entirely.
    bases: tuple[type, ...] = (
        (MIRRORS[parent], native) if parent is not None else (Exception, Object)
    )
    # Cast, not a wider annotation: a metaclass call answers `PoopExcMeta`, and
    # only the bases say the result is an exception class. Every branch above
    # puts a native exception in `bases`, so the claim holds.
    mirror = cast(
        "type[Exception]",
        PoopExcMeta(
            native.__name__,
            bases,
            {"_native": native, "__module__": "builtins", "__slots__": ()},
        ),
    )
    MIRRORS[native.__name__] = mirror
    NATIVE_TO_POOP[native] = mirror


for _native, _parent in _HIERARCHY:
    _build(_native, _parent)


def poop_class_of(exc: BaseException) -> Any:
    """The POOP class answering for `exc` — its mirror, or the nearest one.

    A user's own exception is already a POOP class and answers for itself. An
    unmirrored native (`MemoryError`, say) answers with the closest mirrored
    ancestor rather than leaking the raw class back out.
    """
    for base in type(exc).__mro__:
        if isinstance(base, PoopExcMeta):
            return base
        mirror = NATIVE_TO_POOP.get(base)
        if mirror is not None:
            return mirror
    return MIRRORS["Exception"]
