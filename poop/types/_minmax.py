"""The shared body behind every `min` / `max` message.

Lived in `_iterable_mixin` while only the mixin, `Dict` and `Str` sent it. The
scalar rungs need it too — `Int.max` and `Float.max` take the same `key` their
builtin does — and `_iterable_mixin` imports `Int`, so the helper cannot stay in
a module its own callers sit underneath. Its own home has no POOP imports at
all, which is what lets all five reach it from the top of the file.
"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Name only — importing `none` at runtime would put this module back under
    # the callers it has to stay above.
    from poop.types.none import NoneClass

# The "argument not given" sentinel. Identity is what drives the `default`
# branch below, so every caller must import *this* object rather than build a
# lookalike.
_MISSING: Any = object()


def _minmax(
    func: Callable[..., Any],
    name: str,
    iterable: Any,
    key: Callable[[Any], Any] | NoneClass | None,
    default: Any,
) -> Any:
    """Assemble the optional `key`/`default` kwargs and call `min`/`max`.

    Each caller passes only its own iterable — `Dict`, `Str` and the numeric
    rungs deliberately do not inherit the iterable mixin, and the scalars pass
    the tuple of their operands, which is the single-iterable form CPython's
    `max((a, b), key=f)` already means.

    `key=None` would work at runtime but matches no `min`/`max` overload, so an
    absent one is omitted rather than passed through. "Absent" is `_is_absent`,
    not `is None`: POOP's `None` is a `NoneClass` instance, so the raw identity
    test read the language's own null as a comparison block and answered
    `'NoneType' object is not callable`.

    `name` is the message — `#min` or `#max` — for the empty-collection
    refusal. Read off `func.__name__` it would spell `min`, the free function
    `no_min` forbids two lines earlier in the same program.
    """
    # Imported here, not at the top: this module is imported by `int.py`, and
    # `_unwrap` reaches `none.py` -> `object.py`, which sits above it.
    from poop.types._argument import a_key
    from poop.types._unwrap import _is_absent
    from poop.types.exceptions import MIRRORS

    kwargs: dict[str, Any] = {}
    if not _is_absent(key):
        # Guarded here rather than at five call sites: this is the one place
        # every `min`/`max` key passes through. Before it, a non-block reached
        # CPython's sort and answered `'int' object is not callable` — true of
        # every POOP object, and silent about what was expected.
        kwargs["key"] = a_key(key, name.lstrip("#"))
    if default is not _MISSING:
        kwargs["default"] = default
        return func(iterable, **kwargs)
    # The sentinel *as* the default, rather than catching the `ValueError`
    # CPython raises: its sentence is `min() iterable argument is empty`, and
    # a `ValueError` out of the user's own `key` block would be caught by the
    # same `except` and reported as an empty collection it says nothing about.
    result = func(iterable, default=_MISSING, **kwargs)
    if result is _MISSING:
        raise MIRRORS["ValueError"](
            f"{name} of an empty collection is undefined — send it a default instead"
        )
    return result
