"""The one spelling of "this value's payload, or the value itself".

A leaf module, importing nothing from the package, so every guard can name it
at the top: `_argument.py` sits below `_unwrap.py` in the import graph and
used to spell the same expression inline instead.
"""

from typing import Protocol, overload


class _Wrapped[T](Protocol):
    """A wrapper that keeps its payload in a `_value` slot of a known type.

    Every scalar wrapper declares one — `Int._value: int`, `Str._value: str`,
    `Bytes._value: bytes` — and the protocol reads it, so `_faithful` can
    answer the payload's own type instead of asking the checker to look away.
    A property rather than an attribute: the protocol only ever reads.
    """

    @property
    def _value(self) -> T: ...


@overload
def _faithful[T](value: _Wrapped[T]) -> T: ...
@overload
def _faithful(value: object) -> object: ...
def _faithful(value: object) -> object:
    """Unwrap a *mandatory* argument's `_value`, or return it raw if it has none.

    A POOP value that carries no `_value` — a `List` / `Set` / `Dict` / `Tuple`
    handed where a scalar (`Str` / `Bytes` / `Int`) was expected — reaches the
    underlying Python call unchanged, so Python raises the faithful `TypeError`
    instead of leaking the internal `#_value` name through
    `does_not_understand`. The `object` overload is that fallback, visible: a
    call site holding a wrapper gets its payload's type back, and one holding
    an `object` gets `object`, which an `_argument.py` guard then narrows.
    """
    return getattr(value, "_value", value)
