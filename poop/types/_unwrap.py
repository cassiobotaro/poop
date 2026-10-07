from typing import Any, TypeIs, overload

from poop.types._raw import _faithful
from poop.types.boolean import Boolean
from poop.types.exceptions import MIRRORS
from poop.types.none import NoneClass


def _is_absent(value: object) -> TypeIs[NoneClass | None]:
    # TypeIs (PEP 742) narrows callers: after `if _is_absent(x): ...` the
    # else/fall-through branch sees `x` with NoneClass | None removed, so
    # `x._value` resolves without a per-call-site ignore directive.
    return value is None or isinstance(value, NoneClass)


def _searched(value: object) -> Any:
    """`_faithful`, plus the `Boolean` fold, for a value crossing into raw Python.

    `_faithful` reads `_value`, and `Boolean` is the one wrapper in the language
    that has none — the two rungs of the numeric tower are separate classes, as
    `_index.py` says. Where the unwrapped value is handed to CPython as an
    *index* that costs nothing, because `Boolean.__index__` folds it to 1/0 on
    arrival. Where it is handed over to be compared by **equality** it costs the
    answer: the wrapper crosses intact, meets a raw Python number, and
    `_num_value` has no branch for one, so both directions of the comparison
    decline and the two are unequal.

    `Range` is the only receiver that reaches that case — every other collection
    holds POOP objects, so the comparison is `Int(1) == true` and the tower's own
    fold applies. Its `__init__` and `at` already route through `_index`; this is
    what `includes`, `count` and `index` need, and it cannot be `_index` itself
    because a search must answer `false`/`0` for a foreign value where `_index`
    refuses one.
    """
    if isinstance(value, Boolean):
        return 1 if value else 0
    return _faithful(value)


def _attr_name(name: object) -> str:
    """The raw attribute name behind a `Str`, else CPython's own `TypeError`.

    The `get_attr` / `has_attr` / `set_attr` / `del_attr` family is what
    `no_getattr` offers in place of `getattr`, and it lives on `Object`, so
    every value in the language carries it. Reading `name._value` answered
    `list does not understand #_value` for a non-`Str` name — a POOP internal,
    from the substitute for the very builtin whose leak it was meant to close.
    `getattr(obj, 5)` says `attribute name must be string, not 'int'`; so does
    this, POOP's class names making it read the same way.
    """
    raw = _faithful(name)
    if not isinstance(raw, str):
        raise MIRRORS["TypeError"](
            f"attribute name must be string, not {type(name).__name__!r}"
        )
    return raw


def _unwrap[T](value: object, default: T) -> T:
    if _is_absent(value):
        return default
    # Optional-argument twin of `_faithful`: an absent argument falls back to
    # `default`; a present one unwraps faithfully (raw value reaches Python for
    # a TypeError rather than leaking `#_value`).
    result: Any = _faithful(value)
    return result


def _unwrap_bool(value: object, default: bool) -> bool:
    if _is_absent(value):
        return default
    return bool(value)


# A typed thin alias — a readability shortcut that shares `_unwrap`'s body,
# so Bytes / ByteArray / Str need not re-declare the same 2-line helper.
#
# Note on semantics: it routes through `_unwrap`, which treats Python
# `None` and POOP `NoneClass` alike as absent — user code that passes
# `none` is handled identically to the missing-arg case.


@overload
def _opt_str(value: object, default: str) -> str: ...
@overload
def _opt_str(value: object, default: None = None) -> str | None: ...
def _opt_str(value: object, default: str | None = None) -> str | None:
    """`Str | None` → `str` (with default) or `str | None` (default omitted)."""
    return _unwrap(value, default)
