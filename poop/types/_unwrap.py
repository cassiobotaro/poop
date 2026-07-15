from typing import TypeIs, overload

from poop.types.none import NoneClass


def _is_absent(value: object) -> TypeIs[NoneClass | None]:
    # TypeIs (PEP 742) narrows callers: after `if _is_absent(x): ...` the
    # else/fall-through branch sees `x` with NoneClass | None removed, so
    # `x._value` resolves without a per-call-site ignore directive.
    return value is None or isinstance(value, NoneClass)


def _unwrap[T](value: object, default: T) -> T:
    if _is_absent(value):
        return default
    return getattr(value, "_value")  # noqa: B009


def _unwrap_bool(value: object, default: bool) -> bool:
    if _is_absent(value):
        return default
    return bool(value)


# Typed thin aliases — readability shortcuts that share `_unwrap`'s body,
# so Bytes / ByteArray / Str need not re-declare the same 2-line helper.
#
# Note on semantics: both route through `_unwrap`, which treats Python
# `None` and POOP `NoneClass` alike as absent — user code that passes
# `none` is handled identically to the missing-arg case.


@overload
def _opt_int(value: object, default: int) -> int: ...
@overload
def _opt_int(value: object, default: None = None) -> int | None: ...
def _opt_int(value: object, default: int | None = None) -> int | None:
    """`Int | None` → `int` (with default) or `int | None` (default omitted)."""
    return _unwrap(value, default)


@overload
def _opt_str(value: object, default: str) -> str: ...
@overload
def _opt_str(value: object, default: None = None) -> str | None: ...
def _opt_str(value: object, default: str | None = None) -> str | None:
    """`Str | None` → `str` (with default) or `str | None` (default omitted)."""
    return _unwrap(value, default)
