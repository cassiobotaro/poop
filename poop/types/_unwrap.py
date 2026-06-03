from typing import Any, TypeIs, overload

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


def _opt_timeout(value: object) -> Any:
    """`Float | Int | None` → `float | int | None`; for stdlib timeout kwargs."""
    return _unwrap(value, None)


def _kwargs_from(**named: Any) -> dict[str, Any]:
    """Drop absent values; unwrap survivors via `._value`.

    Treats both Python `None` and POOP `none` as absent, matching
    `_unwrap` / `_unwrap_bool` — otherwise a user-passed `none` (which
    `NoneTransformer` produces from every `None` literal) slips past the
    filter and crashes on `._value`.

        kwargs = _kwargs_from(x=x, y=y)        # builds fresh dict
        kwargs.update(_kwargs_from(x=x, y=y))  # merges into existing dict
    """
    return {k: v._value for k, v in named.items() if not _is_absent(v)}
