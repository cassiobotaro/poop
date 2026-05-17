import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import true
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.struct import Struct, StructNamespace
from poop.types.tuple import Tuple

# --- Module-level shortcuts ---


def test_pack_single_int() -> None:
    packed = StructNamespace.pack(Str(">I"), Int(42))
    assert isinstance(packed, Bytes)
    assert packed._value == b"\x00\x00\x00\x2a"


def test_pack_multiple_values() -> None:
    packed = StructNamespace.pack(Str(">IH"), Int(1), Int(2))
    assert packed._value == b"\x00\x00\x00\x01\x00\x02"


def test_pack_float() -> None:
    packed = StructNamespace.pack(Str(">f"), Float(1.0))
    assert isinstance(packed, Bytes)
    assert len(packed._value) == 4


def test_pack_bool() -> None:
    packed = StructNamespace.pack(Str("?"), true)
    assert packed._value == b"\x01"


def test_pack_bytes() -> None:
    packed = StructNamespace.pack(Str("3s"), Bytes(b"abc"))
    assert packed._value == b"abc"


def test_unpack_int() -> None:
    result = StructNamespace.unpack(Str(">I"), Bytes(b"\x00\x00\x00\x2a"))
    assert isinstance(result, Tuple)
    assert result.at(Int(0)) == Int(42)


def test_unpack_mixed() -> None:
    raw = StructNamespace.pack(Str(">If?"), Int(7), Float(2.5), true)
    result = StructNamespace.unpack(Str(">If?"), raw)
    assert result.at(Int(0)) == Int(7)
    assert isinstance(result.at(Int(1)), Float)
    assert result.at(Int(2)) is true


def test_unpack_returns_wrapped_types() -> None:
    raw = StructNamespace.pack(Str(">B"), Int(255))
    result = StructNamespace.unpack(Str(">B"), raw)
    assert isinstance(result.at(Int(0)), Int)


def test_calcsize_returns_int() -> None:
    size = StructNamespace.calcsize(Str(">IH"))
    assert isinstance(size, Int)
    assert size == Int(6)


def test_unpack_from_offset() -> None:
    buf = Bytes(b"xx\x00\x00\x00\x05")
    result = StructNamespace.unpack_from(Str(">I"), buf, offset=Int(2))
    assert result.at(Int(0)) == Int(5)


def test_unpack_from_default_offset() -> None:
    buf = Bytes(b"\x00\x00\x00\x09")
    result = StructNamespace.unpack_from(Str(">I"), buf)
    assert result.at(Int(0)) == Int(9)


def test_pack_into_bytearray() -> None:
    buf = ByteArray(b"\x00\x00\x00\x00\x00\x00")
    assert StructNamespace.pack_into(Str(">I"), buf, Int(2), Int(7)) is none
    assert bytes(buf._value) == b"\x00\x00\x00\x00\x00\x07"


def test_pack_into_rejects_immutable_bytes() -> None:
    with pytest.raises(TypeError):
        StructNamespace.pack_into(Str(">I"), Bytes(b"\x00" * 4), Int(0), Int(1))  # ty: ignore[invalid-argument-type]


def test_iter_unpack_returns_list_of_tuples() -> None:
    raw = StructNamespace.pack(Str(">II"), Int(1), Int(2))
    result = StructNamespace.iter_unpack(Str(">I"), raw)
    assert isinstance(result, List)
    assert result.len() == Int(2)
    assert result.at(Int(0)) == Tuple(Int(1))
    assert result.at(Int(1)) == Tuple(Int(2))


def test_unpack_format_mismatch_raises() -> None:
    with pytest.raises(StructNamespace.error):
        StructNamespace.unpack(Str(">I"), Bytes(b"\x00"))


# --- Struct class ---


def test_struct_class_pack_round_trips() -> None:
    s = Struct(Str(">If"))
    raw = s.pack(Int(7), Float(1.5))
    result = s.unpack(raw)
    assert result.at(Int(0)) == Int(7)
    assert result.at(Int(1)) == Float(1.5)


def test_struct_class_format_property() -> None:
    s = Struct(Str(">IH"))
    assert s.format == Str(">IH")


def test_struct_class_size_property() -> None:
    s = Struct(Str(">IH"))
    assert s.size == Int(6)


def test_struct_class_pack_into() -> None:
    s = Struct(Str(">I"))
    buf = ByteArray(b"\x00\x00\x00\x00")
    s.pack_into(buf, Int(0), Int(42))
    assert bytes(buf._value) == b"\x00\x00\x00\x2a"


def test_struct_class_unpack_from_offset() -> None:
    s = Struct(Str(">I"))
    buf = Bytes(b"xx\x00\x00\x00\x07")
    result = s.unpack_from(buf, offset=Int(2))
    assert result.at(Int(0)) == Int(7)


def test_struct_class_iter_unpack() -> None:
    s = Struct(Str(">I"))
    raw = StructNamespace.pack(Str(">III"), Int(1), Int(2), Int(3))
    result = s.iter_unpack(raw)
    assert result.len() == Int(3)


# --- Interpreter integration ---


def test_struct_pack_reachable_via_interpreter() -> None:
    Interpreter().run_source('struct.pack(">I", 42).print()')


def test_struct_unpack_reachable_via_interpreter() -> None:
    src = 'raw = struct.pack(">II", 1, 2)\nstruct.unpack(">II", raw).print()\n'
    Interpreter().run_source(src)


def test_struct_class_reachable_via_interpreter() -> None:
    Interpreter().run_source('Struct(">I").size.print()')


def test_struct_calcsize_reachable_via_interpreter() -> None:
    Interpreter().run_source('struct.calcsize(">IH").print()')


# --- Error paths and underused wrapper branches ---


def test_pack_bytearray_value() -> None:
    # Exercises _unwrap_value's ByteArray branch.
    packed = StructNamespace.pack(Str("3s"), ByteArray(b"xyz"))
    assert packed._value == b"xyz"


def test_pack_into_memoryview_buffer() -> None:
    from poop.types.memory_view import MemoryView

    raw = bytearray(b"\x00\x00\x00\x00")
    view = MemoryView(memoryview(raw))
    assert StructNamespace.pack_into(Str(">I"), view, Int(0), Int(9)) is none
    assert bytes(raw) == b"\x00\x00\x00\x09"


def test_unpack_from_bytearray_buffer() -> None:
    buf = ByteArray(b"\x00\x00\x00\x03")
    result = StructNamespace.unpack_from(Str(">I"), buf)
    assert result.at(Int(0)) == Int(3)


def test_unpack_from_rejects_non_buffer() -> None:
    with pytest.raises(TypeError, match="Bytes / ByteArray / MemoryView"):
        StructNamespace.unpack_from(Str(">I"), Str("xxxx"))  # ty: ignore[invalid-argument-type]


def test_pack_into_rejects_non_buffer_writable() -> None:
    with pytest.raises(TypeError, match="writable buffer"):
        StructNamespace.pack_into(Str(">I"), Str("xxxx"), Int(0), Int(1))  # ty: ignore[invalid-argument-type]


def test_struct_class_pack_into_via_memoryview() -> None:
    from poop.types.memory_view import MemoryView

    raw = bytearray(b"\x00\x00\x00\x00")
    view = MemoryView(memoryview(raw))
    s = Struct(Str(">I"))
    s.pack_into(view, Int(0), Int(42))
    assert bytes(raw) == b"\x00\x00\x00\x2a"
