"""The argument guards, read through the programs that reach them.

`tests/test_no_python_wording.py` says what a refusal must *not* say; this
pins what the shared guards in `poop/types/_argument.py` say instead, once per
argument kind, across the receivers that share each one.
"""

import pytest

from poop import Interpreter
from poop.errors import PoopError
from poop.types.boolean import true
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.set import Set
from poop.types.slice import Slice
from poop.types.string import Str
from poop.types.tuple import Tuple


def _failure(source: str) -> str:
    with pytest.raises(PoopError) as info:
        Interpreter().run_source(source + "\n")
    return str(info.value)


@pytest.mark.parametrize(
    ("source", "selector", "role"),
    [
        ('(5).round("x")', "round", "ndigits"),
        ('(2.5).round("x")', "round", "ndigits"),
        ('True.round("x")', "round", "ndigits"),
        ('(5).to_bytes("x")', "to_bytes", "length"),
        ('True.to_bytes("x")', "to_bytes", "length"),
        ('"ab".center("x")', "center", "width"),
        ('b"ab".ljust("x")', "ljust", "width"),
        ('bytearray(b"ab").rjust("x")', "rjust", "width"),
        ('"ab".zfill("x")', "zfill", "width"),
        ('"ab".expandtabs("x")', "expandtabs", "tabsize"),
        ('b"ab".expandtabs("x")', "expandtabs", "tabsize"),
        ('b"ab".hex(":", "x")', "hex", "bytes_per_sep"),
        ('bytearray(b"ab").hex(":", "x")', "hex", "bytes_per_sep"),
        ('memoryview(b"ab").hex(":", "x")', "hex", "bytes_per_sep"),
        ('[1, 2].insert("x", 3)', "insert", "index"),
        ('[1, 2].pop("x")', "pop", "index"),
        ('bytearray(b"ab").insert("x", 3)', "insert", "index"),
        ('bytearray(b"ab").insert(0, "x")', "insert", "byte"),
        ('bytearray(b"ab").pop("x")', "pop", "index"),
        ('bytearray(b"ab").append("x")', "append", "byte"),
        ('bytearray(b"ab").remove("x")', "remove", "byte"),
        ('slice(0, 2).indices("x")', "indices", "length"),
    ],
)
def test_an_integer_argument_names_its_message_and_its_role(
    source: str, selector: str, role: str
) -> None:
    # `'str' object cannot be interpreted as an integer` names neither.
    wanted = f"TypeError: #{selector}'s {role} must be an int, got a str (line 1)"
    assert _failure(source) == wanted


def test_a_mandatory_integer_refuses_a_float_and_none() -> None:
    assert "must be an int, got a float" in _failure('"ab".center(2.5)')
    assert "must be an int, got a NoneType" in _failure('"ab".center(None)')


def test_the_guarded_integers_still_answer() -> None:
    assert Int(1234).round(Int(-2)) == Int(1200)
    assert Float(2.567).round(Int(2)) == Float(2.57)
    assert Float(2.5).round() == Int(2)
    assert Float(2.5).round(none) == Int(2)
    assert Int(5).to_bytes() == Bytes(b"\x05")
    assert Int(5).to_bytes(Int(2)) == Bytes(b"\x00\x05")
    assert Str("ab").center(Int(4)) == Str(" ab ")
    assert Str("a\tb").expandtabs() == Str("a       b")
    assert Str("a\tb").expandtabs(Int(2)) == Str("a b")
    assert Bytes(b"ab").hex(Str(":"), Int(1)) == Str("61:62")
    xs = List(Int(1), Int(2))
    xs.insert(Int(0), Int(9))
    assert xs.pop(Int(0)) == Int(9)
    # A Boolean is an index, as `_index.py` says.
    assert xs.pop(true) == Int(2)
    assert Slice(Int(0), Int(2)).indices(Int(5)) == Tuple(Int(0), Int(2), Int(1))


@pytest.mark.parametrize(
    ("source", "selector"),
    [
        ("[1].zip(5)", "zip"),
        ("zip([1], 5)", "zip"),
        ('"ab".zip(5)', "zip"),
        ("enumerate(5)", "enumerate"),
        ("{1}.union(5)", "union"),
        ("{1}.intersection(5)", "intersection"),
        ("{1}.difference(5)", "difference"),
        ("{1}.symmetric_difference(5)", "symmetric_difference"),
        ("{1}.update(5)", "update"),
        ("{1}.intersection_update(5)", "intersection_update"),
        ("{1}.difference_update(5)", "difference_update"),
        ("{1}.symmetric_difference_update(5)", "symmetric_difference_update"),
        ("{1}.isdisjoint(5)", "isdisjoint"),
        ("{1}.issubset(5)", "issubset"),
        ("frozenset([1]).issuperset(5)", "issuperset"),
        ("frozenset([1]).union(5)", "union"),
        ('{"a": 1}.keys().isdisjoint(5)', "isdisjoint"),
        ('{"a": 1}.items().isdisjoint(5)', "isdisjoint"),
        ('",".join(5)', "join"),
        ('b",".join(5)', "join"),
        ('bytearray(b",").join(5)', "join"),
        ("[1].extend(5)", "extend"),
        ('bytearray(b"a").extend(5)', "extend"),
        ("{}.update(5)", "update"),
        ("dict.fromkeys(5)", "fromkeys"),
    ],
)
def test_a_collection_argument_names_its_message(source: str, selector: str) -> None:
    # `'int' object is not iterable` names no message, and "iterable" is the
    # protocol `no_iter` bans.
    wanted = f"TypeError: #{selector} expects a collection, got an int (line 1)"
    assert _failure(source) == wanted


def test_a_collection_of_pairs_names_the_entry_that_is_not_one() -> None:
    wanted = "TypeError: #update expects key/value pairs, got an int among them"
    assert wanted in _failure("{}.update([1])")


def test_a_byte_array_names_the_element_that_is_not_a_byte() -> None:
    wanted = "TypeError: #extend's byte must be an int, got a str"
    assert wanted in _failure('bytearray(b"a").extend(["x"])')


def test_the_guarded_collections_still_answer() -> None:
    assert Set(Int(1)).union(List(Int(2)), Tuple(Int(3))) == Set(Int(1), Int(2), Int(3))
    assert Str(",").join(List(Str("a"), Str("b"))) == Str("a,b")
    xs = List(Int(1))
    xs.extend(Str("ab"))
    assert xs == List(Int(1), Str("a"), Str("b"))
    raw = ByteArray(bytearray(b"a"))
    raw.extend(Bytes(b"b"))
    raw.extend(List(Int(99)))
    assert raw == ByteArray(bytearray(b"abc"))
    pairs = Dict()
    pairs.update(List(Tuple(Str("a"), Int(1))))
    assert pairs.at(Str("a")) == Int(1)
    assert Dict.fromkeys(Str("ab")).len() == Int(2)


@pytest.mark.parametrize(
    ("source", "selector", "expected"),
    [
        ('"ab".startswith(5)', "startswith", "a str or a tuple of str"),
        ('"ab".endswith(5)', "endswith", "a str or a tuple of str"),
        ('"ab".startswith(("a", 5))', "startswith", "a str or a tuple of str"),
        ('b"ab".startswith(5)', "startswith", "bytes or a tuple of bytes"),
        (
            'bytearray(b"ab").endswith((b"a", 5))',
            "endswith",
            "bytes or a tuple of bytes",
        ),
    ],
)
def test_an_affix_argument_names_its_message(
    source: str, selector: str, expected: str
) -> None:
    # `startswith first arg must be str or a tuple of str, not int` spells the
    # message as a bare word, and "arg" is not a word the language uses.
    wanted = f"TypeError: #{selector} expects {expected}, got an int (line 1)"
    assert _failure(source) == wanted


def test_the_guarded_affixes_still_answer() -> None:
    assert Str("ab").startswith(Str("a")) == true
    assert Str("ab").endswith(Tuple(Str("z"), Str("b"))) == true
    assert Bytes(b"ab").startswith(Tuple(Bytes(b"z"), Bytes(b"a"))) == true
    assert ByteArray(bytearray(b"ab")).endswith(Bytes(b"b")) == true


@pytest.mark.parametrize(
    ("source", "wanted"),
    [
        ('{"a": 1}.keys() | 5', "dict_keys does not understand #| with an int"),
        ('5 & {"a": 1}.keys()', "int does not understand #& with a dict_keys"),
        ('{"a": 1}.items() ^ 5', "dict_items does not understand #^ with an int"),
        ('5 - {"a": 1}.items()', "int does not understand #- with a dict_items"),
        ("xs = [1]\nxs += 5", "list does not understand #+= with an int"),
    ],
)
def test_an_operator_declines_a_scalar_where_a_message_refuses_one(
    source: str, wanted: str
) -> None:
    # An operator's refusal is the operator's sentence, not `a_collection`'s —
    # and not `'int' object is not iterable`.
    assert f"TypeError: {wanted}" in _failure(source)
