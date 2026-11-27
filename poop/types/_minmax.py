"""The shared body behind every `min` / `max` message.

Not in `_iterable_mixin`: the scalar rungs need it too — `Int.max` and
`Float.max` take the same `key` their builtin does — and `_iterable_mixin`
imports `Int`, so the helper cannot live in a module its own callers sit
underneath. Its own home has no POOP imports at all, which is what lets all
four reach it from the top of the file.
"""

from typing import TYPE_CHECKING

from poop.types import mirrors
from poop.types._argument import Key, a_key
from poop.types._sentinel import MISSING

# circular: _unwrap -> boolean -> _minmax
lazy from poop.types._unwrap import _is_absent

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


def _minmax[T, D](
    func: Callable[..., T | D],
    name: str,
    iterable: Iterable[T],
    key: Key[T],
    default: D | MISSING,
) -> T | D:
    """Assemble the optional `key`/`default` kwargs and call `min`/`max`.

    Answers an element, or the default when one was given and the collection
    is empty — `T | D`, which is what each caller's own overload pair says.

    Each caller passes only its own iterable: the mixin its `_iter_items()`
    — `Str` and `Dict` inherit it — and the scalar rungs the tuple of their
    operands, which is the single-iterable form CPython's `max((a, b),
    key=f)` already means.

    `key=None` would work at runtime but matches no `min`/`max` overload, so an
    absent one is omitted rather than passed through. "Absent" is `_is_absent`,
    not `is None`: POOP's `None` is a `NoneClass` instance, so a raw identity
    test would read the language's own null as a comparison block and answer
    `'NoneType' object is not callable`.

    `name` is the message — `#min` or `#max` — for the empty-collection
    refusal. Read off `func.__name__` it would spell `min`, the free function
    `no_min` forbids two lines earlier in the same program.
    """
    kwargs: dict[str, object] = {}
    if not _is_absent(key):
        # Guarded here rather than at each call site: this is the one place
        # every `min`/`max` key passes through. Unguarded, a non-block reaches
        # CPython's sort and answers `'int' object is not callable` — true of
        # every POOP object, and silent about what was expected.
        kwargs["key"] = a_key(key, name.lstrip("#"))
    if default is not MISSING:
        kwargs["default"] = default
        return func(iterable, **kwargs)
    # The sentinel *as* the default, rather than catching the `ValueError`
    # CPython raises: its sentence is `min() iterable argument is empty`, and
    # a `ValueError` out of the user's own `key` block would be caught by the
    # same `except` and reported as an empty collection it says nothing about.
    result = func(iterable, default=MISSING, **kwargs)
    if result is MISSING:
        raise mirrors.ValueError(
            f"{name} of an empty collection is undefined — send it a default instead"
        )
    return result
