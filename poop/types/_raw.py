"""The one spelling of "this value's payload, or the value itself".

A leaf module, importing nothing from the package, so every guard can name it
at the top: `_argument.py` sits below `_unwrap.py` in the import graph and
used to spell the same expression inline instead.
"""

from typing import Any


def _faithful(value: object) -> Any:
    """Unwrap a *mandatory* argument's `_value`, or return it raw if it has none.

    A POOP value that carries no `_value` — a `List` / `Set` / `Dict` / `Tuple`
    handed where a scalar (`Str` / `Bytes` / `Int`) was expected — reaches the
    underlying Python call unchanged, so Python raises the faithful `TypeError`
    instead of leaking the internal `#_value` name through
    `does_not_understand`. Returns `Any` so the raw fallback slots into a
    `str` / `bytes` / `int` parameter without a per-call-site ignore.
    """
    return getattr(value, "_value", value)
