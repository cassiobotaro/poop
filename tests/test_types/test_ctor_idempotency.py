"""Value-wrapping ctors are idempotent.

`Str(Str(x))`, `Int(Int(x))`, etc. unwrap instead of nesting. Without
this the `x = str; x("hi")` pattern (where `str` is rewritten to `Str`
at parse time) would produce a Str whose `_value` is itself a Str.
"""

import pytest

from poop import Interpreter
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.memory_view import MemoryView
from poop.types.path import Path
from poop.types.string import Str


@pytest.mark.parametrize(
    ("ctor", "primitive"),
    [
        (Str, "hi"),
        (Int, 42),
        (Float, 3.14),
        (Bytes, b"hi"),
        (ByteArray, bytearray(b"hi")),
        (MemoryView, memoryview(b"hi")),
        (Complex, complex(1, 2)),
    ],
)
def test_ctor_unwraps_own_type(ctor: type, primitive: object) -> None:
    inner = ctor(primitive)
    outer = ctor(inner)
    assert outer._value == inner._value


def test_path_ctor_unwraps_own_type() -> None:
    inner = Path(Str("tmp.txt"))
    outer = Path(inner)
    assert outer._path == inner._path


def test_aliased_str_constructor_works_end_to_end() -> None:
    """`x = str; x("hi").upper()` was broken before idempotent ctors."""
    Interpreter().run_source('x = str\nx("hi").upper().print()')
