import operator
from typing import SupportsIndex

from poop.types._raw import _faithful
from poop.types._sentinel import NOT_A_COUNT, NotACount
from poop.types.boolean import Boolean


def _repeat_count(other: object) -> int | NotACount:
    """Repeat count for sequence multiplication, or `NOT_A_COUNT`.

    ``bool`` is an ``int`` subclass — ``"ab" * True == "ab"`` — but a POOP
    ``Boolean`` has no ``_value`` slot, so fold it explicitly. That half is what
    this helper is really for and is unchanged.

    The other half used to unwrap anything at all and hand it to the wrapped
    sequence's ``__mul__``, "so [it] raises CPython's faithful ``can't multiply
    sequence by non-int`` ``TypeError``". Faithful to CPython is exactly what
    the wording sweep overturned, and that sentence names "sequence" —
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
    if isinstance(other, Boolean):
        return int(bool(other))
    raw = _faithful(other)
    # `__index__`, not `isinstance(raw, int)`: CPython repeats a sequence by
    # anything with an index, and POOP's own `Index` rung is exactly that.
    # `operator.index` is the same question with an `int` for an answer.
    if isinstance(raw, SupportsIndex):
        return operator.index(raw)
    return NOT_A_COUNT
