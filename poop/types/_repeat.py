from typing import Any

# Answered for an operand that is no repeat count at all, so the caller can
# return `NotImplemented` and let CPython raise the shape `poop_message`
# rewrites. A sentinel rather than `None`, which is a legitimate `_value`.
NOT_A_COUNT: Any = object()


def _repeat_count(other: object) -> Any:
    """Repeat count for sequence multiplication, or `NOT_A_COUNT`.

    ``bool`` is an ``int`` subclass — ``"ab" * True == "ab"`` — but a POOP
    ``Boolean`` has no ``_value`` slot, so fold it explicitly. That half is what
    this helper is really for and is unchanged.

    The other half used to unwrap anything at all and hand it to the wrapped
    sequence's ``__mul__``, "so [it] raises CPython's faithful ``can't multiply
    sequence by non-int`` ``TypeError``". Faithful to CPython is exactly what
    proposal 10 spent an item overturning, and that sentence names "sequence" —
    a Python protocol, not a receiver — quotes the class the CPython way, and
    describes the operator as a type-level protocol rather than a message, which
    the wording sweep bans under `operator-as-protocol`:

        ([1, 2] + "a")   # list does not understand #+ with a str
        ([1, 2] * "a")   # can't multiply sequence by non-int of type 'str'

    ``__add__`` shows the machinery was already there: it answers
    ``NotImplemented`` for a foreign operand, CPython raises ``unsupported
    operand type(s) for +``, and ``poop_message`` rewrites that shape into
    ``binary_refusal``'s sentence. ``*`` never reached it, because the *inner*
    multiplication raised a shape ``poop_message`` does not match. Answering the
    sentinel here puts ``*`` on the same path, with no new wording.

    Five wrappers answer ``*`` (``Str``, ``List``, ``Tuple``, ``Bytes``,
    ``ByteArray``) against fourteen operand kinds — 95 sites, one operator.
    """
    from poop.types.boolean import Boolean

    if isinstance(other, Boolean):
        return int(bool(other))
    raw = getattr(other, "_value", other)
    # `__index__`, not `isinstance(raw, int)`: CPython repeats a sequence by
    # anything with an index, and POOP's own `Index` rung is exactly that.
    if isinstance(raw, int) or hasattr(raw, "__index__"):
        return raw
    return NOT_A_COUNT
