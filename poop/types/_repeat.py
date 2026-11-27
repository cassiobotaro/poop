import operator
from typing import SupportsIndex

from poop.types._raw import _faithful
from poop.types._sentinel import NOT_A_COUNT


def _repeat_count(other: object) -> int | NOT_A_COUNT:
    """Repeat count for sequence multiplication, or `NOT_A_COUNT`.

    ``bool`` is an ``int`` subclass — ``"ab" * True == "ab"`` — and a POOP
    ``Boolean`` has no ``_value`` slot, so ``_faithful`` hands it over whole and
    its ``__index__`` folds it to 1/0 below, with every other index.

    Anything else answers the sentinel, and the wrapper's ``__mul__`` answers
    ``NotImplemented``, the path ``__add__`` takes for a foreign operand:
    CPython raises ``unsupported operand type(s)``, and ``poop_message``
    rewrites that shape into ``binary_refusal``'s sentence:

        ([1, 2] + "a")   # list does not understand #+ with a str
        ([1, 2] * "a")   # list does not understand #* with a str

    Handing the operand to the wrapped sequence's own ``__mul__`` instead
    raises ``can't multiply sequence by non-int of type 'str'``, a shape
    ``poop_message`` does not match. That sentence names "sequence" — a Python
    protocol, not a receiver — quotes the class the CPython way, and describes
    the operator as a type-level protocol rather than a message, which
    ``tests/test_no_python_wording.py`` forbids as `operator-as-protocol`.

    ``Str``, ``List``, ``Tuple``, ``Bytes`` and ``ByteArray`` answer ``*``
    through here.
    """
    raw = _faithful(other)
    # `__index__`, not `isinstance(raw, int)`: CPython repeats a sequence by
    # anything with an index, and POOP's own `Index` rung is exactly that.
    # `operator.index` is the same question with an `int` for an answer.
    if isinstance(raw, SupportsIndex):
        return operator.index(raw)
    return NOT_A_COUNT
