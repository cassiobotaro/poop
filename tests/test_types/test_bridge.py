from poop.types._bridge import to_poop, to_python
from poop.types.boolean import Boolean, false, true
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.complex import Complex
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.set import Set
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- to_python ---


def test_to_python_none() -> None:
    assert to_python(none) is None


def test_to_python_boolean_true() -> None:
    result = to_python(true)
    assert result is True
    assert isinstance(result, bool)


def test_to_python_boolean_false() -> None:
    assert to_python(false) is False


def test_to_python_int() -> None:
    result = to_python(Int(42))
    assert result == 42
    assert isinstance(result, int)
    assert not isinstance(result, bool)


def test_to_python_float() -> None:
    assert to_python(Float(3.14)) == 3.14


def test_to_python_str() -> None:
    assert to_python(Str("hello")) == "hello"


def test_to_python_list() -> None:
    result = to_python(List(Int(1), Str("a"), true))
    assert result == [1, "a", True]


def test_to_python_tuple() -> None:
    result = to_python(Tuple(Int(1), Str("a")))
    assert result == (1, "a")
    assert isinstance(result, tuple)


def test_to_python_dict() -> None:
    d = Dict().at_put(Str("k"), Int(1))
    assert to_python(d) == {"k": 1}


def test_to_python_nested() -> None:
    inner = Dict().at_put(Str("n"), List(Int(1), Int(2)))
    outer = List(inner, none, Str("x"))
    assert to_python(outer) == [{"n": [1, 2]}, None, "x"]


def test_to_python_opaque_pass_through() -> None:
    class Marker:
        pass

    m = Marker()
    assert to_python(m) is m


def test_to_python_bytes() -> None:
    result = to_python(Bytes(b"hi"))
    assert result == b"hi"
    assert isinstance(result, bytes)


def test_to_python_bytearray() -> None:
    result = to_python(ByteArray(b"hi"))
    assert result == bytearray(b"hi")
    assert isinstance(result, bytearray)


def test_to_python_set() -> None:
    result = to_python(Set(Int(1), Int(2)))
    assert result == {1, 2}
    assert isinstance(result, set)


def test_to_python_frozen_set() -> None:
    result = to_python(FrozenSet(Int(1), Int(2)))
    assert result == frozenset({1, 2})
    assert isinstance(result, frozenset)


# --- to_poop ---


def test_to_poop_none() -> None:
    assert to_poop(None) is none


def test_to_poop_bool_true() -> None:
    assert to_poop(True) is true


def test_to_poop_bool_false() -> None:
    assert to_poop(False) is false


def test_to_poop_int() -> None:
    assert to_poop(42) == Int(42)


def test_to_poop_float() -> None:
    assert to_poop(3.14) == Float(3.14)


def test_to_poop_str() -> None:
    assert to_poop("hello") == Str("hello")


def test_to_poop_list() -> None:
    assert to_poop([1, "a", True]) == List(Int(1), Str("a"), true)


def test_to_poop_tuple() -> None:
    assert to_poop((1, "a")) == Tuple(Int(1), Str("a"))


def test_to_poop_dict() -> None:
    result = to_poop({"k": 1})
    assert isinstance(result, Dict)
    assert result.at(Str("k")) == Int(1)


def test_to_poop_nested() -> None:
    result = to_poop({"n": [1, 2]})
    assert result.at(Str("n")) == List(Int(1), Int(2))


def test_to_poop_opaque_pass_through() -> None:
    class Marker:
        pass

    m = Marker()
    assert to_poop(m) is m


def test_to_poop_bytes() -> None:
    result = to_poop(b"hi")
    assert isinstance(result, Bytes)
    assert result == Bytes(b"hi")


def test_to_poop_bytearray() -> None:
    result = to_poop(bytearray(b"hi"))
    assert isinstance(result, ByteArray)
    assert result._value == bytearray(b"hi")


def test_to_poop_set() -> None:
    result = to_poop({1, 2})
    assert isinstance(result, Set)
    assert result.len() == Int(2)


def test_to_poop_frozen_set() -> None:
    result = to_poop(frozenset({1, 2}))
    assert isinstance(result, FrozenSet)
    assert result.len() == Int(2)


def test_round_trip_python_poop_python() -> None:
    src = {"a": 1, "b": [1.5, "x", True, None]}
    assert to_python(to_poop(src)) == src


def test_to_poop_bool_not_misclassified_as_int() -> None:
    assert to_poop(True) is true
    assert isinstance(to_poop(True), Boolean)


def test_to_python_NoneClass_instance() -> None:
    assert to_python(NoneClass()) is None


def test_to_python_unwraps_complex() -> None:
    # The scalar rung the ladder skipped: left wrapped, a Complex reached
    # `str.format` as a POOP object and every non-empty spec was refused.
    assert to_python(Complex(complex(1, 2))) == complex(1, 2)


def test_to_poop_wraps_complex() -> None:
    result = to_poop(complex(1, 2))
    assert isinstance(result, Complex)
    assert result._value == complex(1, 2)
