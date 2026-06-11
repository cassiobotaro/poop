import pytest

from poop.interpreter import Interpreter
from poop.types.array import Array, ArrayNamespace
from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str

# --- Construction ---


def test_array_empty_int() -> None:
    a = Array(Str("i"))
    assert a.len() == Int(0)
    assert a.typecode == Str("i")


def test_array_from_list() -> None:
    a = Array(Str("i"), List(Int(1), Int(2), Int(3)))
    assert a.len() == Int(3)
    assert a.at(Int(0)) == Int(1)
    assert a.at(Int(2)) == Int(3)


def test_array_float_typecode() -> None:
    a = Array(Str("d"), List(Float(1.5), Float(2.5)))
    assert a.at(Int(0)) == Float(1.5)
    assert isinstance(a.at(Int(0)), Float)


def test_array_unicode_typecode_rejected() -> None:
    # 'u' is deprecated upstream; POOP omits it deliberately.
    with pytest.raises(ValueError):
        Array(Str("u"), List(Int(0)))


def test_array_typecode_mismatch_raises() -> None:
    with pytest.raises(TypeError):
        Array(Str("i"), List(Float(1.5)))


def test_array_itemsize() -> None:
    a = Array(Str("i"))
    assert isinstance(a.itemsize, Int)
    assert a.itemsize._value > 0


# --- Sequence operations ---


def test_array_append() -> None:
    a = Array(Str("i"))
    assert a.append(Int(42)) is none
    assert a.at(Int(0)) == Int(42)


def test_array_extend_with_list() -> None:
    a = Array(Str("i"), List(Int(1)))
    a.extend(List(Int(2), Int(3)))
    assert a.len() == Int(3)


def test_array_extend_with_array() -> None:
    a = Array(Str("i"), List(Int(1)))
    b = Array(Str("i"), List(Int(2), Int(3)))
    a.extend(b)
    assert a.len() == Int(3)


def test_array_insert() -> None:
    a = Array(Str("i"), List(Int(1), Int(3)))
    a.insert(Int(1), Int(2))
    assert a.at(Int(1)) == Int(2)


def test_array_pop_default() -> None:
    a = Array(Str("i"), List(Int(1), Int(2), Int(3)))
    assert a.pop() == Int(3)
    assert a.len() == Int(2)


def test_array_pop_index() -> None:
    a = Array(Str("i"), List(Int(1), Int(2), Int(3)))
    assert a.pop(Int(0)) == Int(1)


def test_array_remove() -> None:
    a = Array(Str("i"), List(Int(1), Int(2), Int(3)))
    a.remove(Int(2))
    assert a.at(Int(1)) == Int(3)


def test_array_count() -> None:
    a = Array(Str("i"), List(Int(1), Int(2), Int(2), Int(3)))
    assert a.count(Int(2)) == Int(2)


def test_array_index() -> None:
    a = Array(Str("i"), List(Int(10), Int(20), Int(30)))
    assert a.index(Int(20)) == Int(1)


def test_array_reverse() -> None:
    a = Array(Str("i"), List(Int(1), Int(2), Int(3)))
    a.reverse()
    assert a.at(Int(0)) == Int(3)


def test_array_slice() -> None:
    a = Array(Str("i"), List(Int(0), Int(1), Int(2), Int(3), Int(4)))
    result = a.slice(Int(1), Int(4))
    assert isinstance(result, Array)
    assert result.len() == Int(3)


def test_array_slice_open_ended() -> None:
    # proposal 143: open-ended slice with a POOP `none` stop.
    a = Array(Str("i"), List(Int(0), Int(1), Int(2), Int(3), Int(4)))
    result = a.slice(Int(2), none)
    assert isinstance(result, Array)
    assert result.len() == Int(3)


def test_array_includes() -> None:
    a = Array(Str("i"), List(Int(1), Int(2)))
    assert a.includes(Int(2)) is true
    assert a.includes(Int(99)) is false


# --- Conversion ---


def test_array_tobytes_round_trip() -> None:
    a = Array(Str("i"), List(Int(1), Int(2), Int(3)))
    buf = a.tobytes()
    assert isinstance(buf, Bytes)
    b = Array(Str("i"), buf)
    assert b.len() == Int(3)


def test_array_tolist() -> None:
    a = Array(Str("i"), List(Int(1), Int(2), Int(3)))
    items = a.tolist()
    assert isinstance(items, List)
    assert items == List(Int(1), Int(2), Int(3))


def test_array_frombytes() -> None:
    a = Array(Str("i"), List(Int(1)))
    b = Array(Str("i"), List(Int(2), Int(3))).tobytes()
    a.frombytes(b)
    assert a.len() == Int(3)


def test_array_fromlist() -> None:
    a = Array(Str("i"), List(Int(1)))
    a.fromlist(List(Int(2), Int(3)))
    assert a.len() == Int(3)


# --- Iteration ---


def test_array_do() -> None:
    a = Array(Str("i"), List(Int(1), Int(2), Int(3)))
    collected: list[int] = []
    a.do(lambda v: collected.append(v._value))  # ty: ignore[unresolved-attribute]
    assert collected == [1, 2, 3]


def test_array_iter() -> None:
    a = Array(Str("i"), List(Int(1), Int(2)))
    assert list(a) == [Int(1), Int(2)]


# --- Namespace ---


def test_array_typecodes_constant() -> None:
    assert isinstance(ArrayNamespace.typecodes, Str)
    assert "i" in ArrayNamespace.typecodes._value


# --- Interpreter integration ---


def test_array_class_reachable_via_interpreter() -> None:
    Interpreter().run_source('Array("i", [1, 2, 3]).len().print()')


def test_array_namespace_reachable_via_interpreter() -> None:
    Interpreter().run_source("array.typecodes.print()")
