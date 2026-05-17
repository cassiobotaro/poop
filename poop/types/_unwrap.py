from typing import Any

from poop.types.none import NoneClass


def _is_absent(value: object) -> bool:
    return value is None or isinstance(value, NoneClass)


def _unwrap[T](value: object, default: T) -> T:
    if _is_absent(value):
        return default
    return getattr(value, "_value")  # noqa: B009


def _unwrap_bool(value: object, default: bool) -> bool:
    if _is_absent(value):
        return default
    return bool(value)


# Typed thin aliases — readability shortcuts that share `_unwrap`'s body.
# Centralising them here keeps namespace wrappers from re-declaring the
# same 2-line helper per module.
#
# Note on semantics: all aliases route through `_unwrap` / `_unwrap_bool`,
# which treat both Python `None` and POOP `NoneClass` as absent. This is
# slightly wider than the per-file locals they replaced (which often only
# checked Python `None`) but is the right call for POOP — user code that
# passes `none` should be handled identically to the missing-arg case.


def _b(value: object, default: bool) -> bool:
    """`Boolean | None` → `bool` with default; alias of `_unwrap_bool`."""
    return _unwrap_bool(value, default)


def _i(value: object, default: int) -> int:
    """`Int | None` → `int` with default."""
    return _unwrap(value, default)


def _opt_int(value: object, default: int) -> int:
    """Same as `_i` — kept for parity with stdlib wrapper call sites."""
    return _unwrap(value, default)


def _opt_str(value: object, default: str) -> str:
    """`Str | None` → `str` with default."""
    return _unwrap(value, default)


def _opt_timeout(value: object) -> Any:
    """`Float | Int | None` → `float | int | None`; for stdlib timeout kwargs."""
    return _unwrap(value, None)
