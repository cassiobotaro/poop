from typing import Any


def _repeat_count(other: object) -> Any:
    """Repeat count for sequence multiplication, folding ``Boolean`` to 1/0.

    ``bool`` is an ``int`` subclass — ``"ab" * True == "ab"`` — but a POOP
    ``Boolean`` has no ``_value`` slot, so fold it explicitly. Any other operand
    is unwrapped to its underlying value (or passed through) so the wrapped
    sequence's ``__mul__`` raises CPython's faithful
    ``can't multiply sequence by non-int`` ``TypeError`` for non-integers.
    """
    from poop.types.boolean import Boolean

    if isinstance(other, Boolean):
        return int(bool(other))
    return getattr(other, "_value", other)
