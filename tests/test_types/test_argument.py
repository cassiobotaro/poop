"""The argument guards, read through the programs that reach them.

`tests/test_no_python_wording.py` says what a refusal must *not* say; this
pins what the shared guards in `poop/types/_argument.py` say instead, once per
argument kind, across the receivers that share each one.
"""

import pytest

from poop import Interpreter
from poop.errors import PoopError
from poop.types.boolean import true
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
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
