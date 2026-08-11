"""A boolean is 1/0 to every receiver that looks for one.

``bool`` is an ``int`` subclass in CPython, so ``[1, 3, 5].index(True)`` is
``0`` and ``1 in range(1, 6, 2)`` is ``True``. POOP's ``Boolean`` is not an
``Int`` subclass — ``_index.py`` states why — so each receiver has to fold it
back, and one of them did not. ``Range`` is the only wrapper holding raw Python
numbers, so a ``Boolean`` handed to its searches crossed into a native ``range``
intact and compared unequal to every element it should have matched.

A per-receiver assertion could not have caught that: the rule is *agreement*
across receivers, and the failing one answered a self-consistent set of wrong
answers. This sends one boolean to every receiver that answers a search and
requires it to agree with the ``Int`` it folds to.
"""

import pytest

from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.range import Range
from poop.types.set import Set
from poop.types.tuple import Tuple


def _dict_holding_zero_and_one() -> Dict:
    keyed = Dict()
    keyed.at_put(Int(0), Int(9))
    keyed.at_put(Int(1), Int(8))
    return keyed


# Each receiver holds 0 and 1, so both folds have something to find and
# something to miss.
_INCLUDES = [
    List(Int(0), Int(1)),
    Tuple(Int(0), Int(1)),
    Set(Int(0), Int(1)),
    FrozenSet(Int(0), Int(1)),
    Range(Int(0), Int(1)),
    Bytes(b"\x00\x01"),
    _dict_holding_zero_and_one(),
]

_SEARCHES = [
    List(Int(0), Int(1)),
    Tuple(Int(0), Int(1)),
    Range(Int(0), Int(1)),
    Bytes(b"\x00\x01"),
]


@pytest.mark.parametrize("receiver", _INCLUDES, ids=lambda r: type(r).__name__)
@pytest.mark.parametrize(("flag", "folded"), [(true, Int(1)), (false, Int(0))])
def test_includes_agrees_with_the_int_the_boolean_folds_to(
    receiver: object, flag: object, folded: Int
) -> None:
    assert receiver.includes(flag) == receiver.includes(folded)  # ty: ignore[unresolved-attribute]


@pytest.mark.parametrize("receiver", _SEARCHES, ids=lambda r: type(r).__name__)
@pytest.mark.parametrize(("flag", "folded"), [(true, Int(1)), (false, Int(0))])
def test_count_agrees_with_the_int_the_boolean_folds_to(
    receiver: object, flag: object, folded: Int
) -> None:
    assert receiver.count(flag) == receiver.count(folded)  # ty: ignore[unresolved-attribute]


@pytest.mark.parametrize("receiver", _SEARCHES, ids=lambda r: type(r).__name__)
@pytest.mark.parametrize(("flag", "folded"), [(true, Int(1)), (false, Int(0))])
def test_index_agrees_with_the_int_the_boolean_folds_to(
    receiver: object, flag: object, folded: Int
) -> None:
    assert receiver.index(flag) == receiver.index(folded)  # ty: ignore[unresolved-attribute]


@pytest.mark.parametrize("receiver", _INCLUDES, ids=lambda r: type(r).__name__)
def test_a_boolean_is_found_at_all(receiver: object) -> None:
    # The agreement assertions above hold vacuously if a receiver answers
    # "absent" for both spellings. Both values really are present.
    assert receiver.includes(true) == true  # ty: ignore[unresolved-attribute]
    assert receiver.includes(false) == true  # ty: ignore[unresolved-attribute]
