"""`at` answers POOP's wording, not CPython's, on every wrapper that has one.

The failures used to name the construct POOP forbids — `list indices` and
`string index` describe subscripting, which `no_subscript` bans — or, for a
missing key, carried no sentence at all. One test per wrapper would leave the
next one free to regress, so the sweep drives them off a table.
"""

from typing import Any

import pytest

from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.mapping_proxy import MappingProxy
from poop.types.memory_view import MemoryView
from poop.types.range import Range
from poop.types.string import Str
from poop.types.tuple import Tuple

_SEQUENCES = [
    (Str("abc"), "str", 3),
    (List(Int(1), Int(2)), "list", 2),
    (Tuple(Int(1), Int(2)), "tuple", 2),
    (Bytes(b"ab"), "bytes", 2),
    (ByteArray(bytearray(b"ab")), "bytearray", 2),
    (Range(Int(0), Int(2)), "range", 3),
    (MemoryView(memoryview(b"ab")), "memoryview", 2),
]


@pytest.mark.parametrize(("receiver", "name", "size"), _SEQUENCES, ids=lambda a: str(a))
def test_at_out_of_range_names_the_receiver_and_its_size(
    receiver: Any, name: str, size: int
) -> None:
    expected = f"{name} has no element at 9 — it has {size} elements"
    with pytest.raises(IndexError, match=rf"^{expected}$"):
        receiver.at(Int(9))


@pytest.mark.parametrize(("receiver", "name", "size"), _SEQUENCES, ids=lambda a: str(a))
def test_at_with_a_non_index_names_the_message_not_the_subscript(
    receiver: Any, name: str, size: int
) -> None:
    expected = f"{name}.at expects an int index, got a str"
    with pytest.raises(TypeError, match=rf"^{expected}$"):
        receiver.at(Str("x"))


def test_at_on_an_empty_receiver_says_so() -> None:
    with pytest.raises(IndexError, match=r"^list has no element at 0 — it is empty$"):
        List().at(Int(0))


def test_at_on_a_single_element_receiver_does_not_pluralise() -> None:
    with pytest.raises(
        IndexError, match=r"^list has no element at 4 — it has 1 element$"
    ):
        List(Int(1)).at(Int(4))


def test_dict_at_answers_a_sentence_not_the_key_repr() -> None:
    # CPython answered the bare `'b'` — a repr with nothing to say a lookup
    # failed, and Python's quoting on a POOP string.
    d = Dict()
    d._data[Str("a")] = Int(1)
    with pytest.raises(KeyError, match=r"^dict has no key 'b'$"):
        d.at(Str("b"))


def test_mapping_proxy_at_names_the_proxy_not_the_dict_behind_it() -> None:
    d = Dict()
    d._data[Str("a")] = Int(1)
    proxy = MappingProxy(d)
    with pytest.raises(KeyError, match=r"^mappingproxy has no key 'b'$"):
        proxy.at(Str("b"))


def test_dict_at_leaves_an_unhashable_key_to_cpython() -> None:
    # That failure is about the key, not the lookup, and its wording is
    # already POOP's — a Dict has keys.
    with pytest.raises(TypeError, match="as a dict key"):
        Dict().at(List(Int(1)))


def test_list_pop_out_of_range_reuses_at_s_wording() -> None:
    # `pop index out of range`: the method named as a Python call, and no
    # receiver in the sentence.
    with pytest.raises(IndexError, match=r"^list has no element at 9 — it has 2"):
        List(Int(1), Int(2)).pop(Int(9))


def test_list_pop_on_an_empty_list_names_the_receiver() -> None:
    with pytest.raises(
        IndexError, match=r"^list has no element to remove — it is empty$"
    ):
        List().pop()


def test_list_index_of_a_missing_value_states_the_value() -> None:
    # `list.index(x): x not in list` spelt the message as a Python call and
    # used a placeholder where the value the reader passed belongs.
    with pytest.raises(ValueError, match=r"^list has no element equal to 9$"):
        List(Int(1)).index(Int(9))


def test_list_index_with_bounds_states_the_value_too() -> None:
    with pytest.raises(ValueError, match=r"^list has no element equal to 1$"):
        List(Int(1), Int(2)).index(Int(1), Int(1), Int(2))


def test_tuple_index_of_a_missing_value_names_the_tuple() -> None:
    with pytest.raises(ValueError, match=r"^tuple has no element equal to 9$"):
        Tuple(Int(1)).index(Int(9))


def test_list_remove_of_a_missing_value_states_the_value() -> None:
    with pytest.raises(ValueError, match=r"^list has no element equal to 9$"):
        List(Int(1)).remove(Int(9))


def test_slice_with_a_non_index_bound_names_the_bound() -> None:
    # `slice indices must be integers or None or have an __index__ method`
    # named subscripting and a banned dunder in one breath.
    from poop.types.slice import Slice

    # Deliberately ill-typed: the point is what a program is told when it
    # writes this, and `ty` is right that it should not.
    bound: Any = Str("a")
    with pytest.raises(TypeError, match=r"^slice bounds must be int, got a str$"):
        Str("abc").slice(Slice(bound, Int(2)))
