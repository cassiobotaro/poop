"""`at`'s failures, worded as POOP rather than as Python.

`at` is POOP's substitute for subscripting, and every wrapper implemented it by
handing the index straight to CPython — so the failure a learner read was
Python's, about the construct POOP forbids:

    "abc".at(10)     ->  IndexError: string index out of range
    [1, 2].at("x")   ->  TypeError: list indices must be integers or slices, not str
    {"a": 1}.at("b") ->  KeyError: 'b'

`list indices` and `string index` describe subscripting, which `no_subscript`
bans; the third is a bare `repr` with no sentence at all. The wording belongs to
whoever owns the operation, and nine wrappers own the same one, so it lives here
instead of being written out nine times.
"""

from __future__ import annotations

from typing import Any

from poop.types.exceptions import MIRRORS


def _size(count: int) -> str:
    if count == 0:
        return "it is empty"
    return f"it has {count} element" if count == 1 else f"it has {count} elements"


def no_element_at(receiver: object, items: Any, index: Any) -> Exception:
    """The mirrored `IndexError` for an index the receiver has no element at.

    Answers the exception rather than raising it, so a call site reads
    `raise no_element_at(...) from None` — the `from None` is the point, and it
    has to be written where the original is caught.
    """
    return MIRRORS["IndexError"](
        f"{type(receiver).__name__} has no element at {index} — {_size(len(items))}"
    )


def no_element_equal_to(receiver: object, value: Any) -> Exception:
    """The mirrored `ValueError` for a value the receiver does not hold.

    CPython spelled this as `list.index(x): x not in list` — the method written
    as a Python call rather than sent as a message, and the placeholder `x`
    where the value the reader passed belongs.
    """
    return MIRRORS["ValueError"](
        f"{type(receiver).__name__} has no element equal to {value!r}"
    )


def at_index(items: Any, index: Any, receiver: object) -> Any:
    """`items[index]`, with POOP's wording for the two ways it can fail.

    `receiver` is the POOP object the message was sent to — the same thing as
    `items` for most wrappers, but a `Range` materializes its sequence first,
    and a name read off the wrong one would say `range` where the reader wrote
    a `Range`, or vice versa.
    """
    try:
        return items[index]
    except IndexError:
        raise no_element_at(receiver, items, index) from None
    except TypeError:
        # The only TypeError a sequence lookup raises: the index is not one.
        raise MIRRORS["TypeError"](
            f"{type(receiver).__name__}.at expects an int index, "
            f"got a {type(index).__name__}"
        ) from None


def at_key(data: Any, key: Any, receiver: object) -> Any:
    """`data[key]`, answering a sentence instead of the missing key's repr.

    An unhashable key is left to CPython: that failure is about the key, not
    about the lookup, and its message (`cannot use 'list' as a dict key`) is
    already in POOP's vocabulary — `Dict` has keys.
    """
    try:
        return data[key]
    except KeyError:
        raise MIRRORS["KeyError"](
            f"{type(receiver).__name__} has no key {key!r}"
        ) from None
