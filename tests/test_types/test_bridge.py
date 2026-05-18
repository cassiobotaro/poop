import pytest

from poop.types._bridge import bridge, to_poop, to_python
from poop.types.block import Block
from poop.types.boolean import Boolean, false, true
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
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


def test_round_trip_python_poop_python() -> None:
    src = {"a": 1, "b": [1.5, "x", True, None]}
    assert to_python(to_poop(src)) == src


# --- bridge ---


def test_bridge_positional_args_are_wrapped() -> None:
    captured: list[object] = []

    def body(x: object, y: object) -> object:
        captured.extend([x, y])
        return Int(0)

    adapter = bridge(Block(body))
    adapter(1, "hello")

    assert captured[0] == Int(1)
    assert isinstance(captured[0], Int)
    assert captured[1] == Str("hello")
    assert isinstance(captured[1], Str)


def test_bridge_keyword_args_are_wrapped() -> None:
    captured: dict[str, object] = {}

    def body(*, x: object, y: object) -> object:
        captured["x"] = x
        captured["y"] = y
        return none

    adapter = bridge(Block(body))
    adapter(x=42, y=[1, 2])

    assert captured["x"] == Int(42)
    assert captured["y"] == List(Int(1), Int(2))


def test_bridge_unwraps_return_value() -> None:
    adapter = bridge(Block(lambda x: x + Int(1)))
    result = adapter(5)
    assert result == 6
    assert isinstance(result, int)


def test_bridge_unwraps_complex_return() -> None:
    adapter = bridge(Block(lambda: Dict().at_put(Str("k"), List(Int(1), true))))
    assert adapter() == {"k": [1, True]}


def test_bridge_wrap_args_false_passes_raw() -> None:
    captured: list[object] = []

    def body(x: object) -> object:
        captured.append(x)
        return none

    adapter = bridge(Block(body), wrap_args=False)
    raw = {"not": "wrapped"}
    adapter(raw)
    assert captured[0] is raw


def test_bridge_unwrap_return_false_passes_poop() -> None:
    poop_value = List(Int(1), Int(2))
    adapter = bridge(Block(lambda: poop_value), unwrap_return=False)
    assert adapter() is poop_value


def test_bridge_propagates_python_exception() -> None:
    def body(_: object) -> object:
        raise ValueError("boom")

    adapter = bridge(Block(body))
    with pytest.raises(ValueError, match="boom"):
        adapter(0)


def test_bridge_propagates_poop_raise() -> None:
    # Mirrors what `KeyError.raise_("msg")` lowers to.
    def body() -> object:
        raise KeyError("nope")

    adapter = bridge(Block(body))
    with pytest.raises(KeyError, match="nope"):
        adapter()


def test_bridge_accepts_plain_callable() -> None:
    adapter = bridge(lambda x: x.upper() if isinstance(x, Str) else x)
    assert adapter("hi") == "HI"


def test_bridge_opaque_arg_pass_through() -> None:
    class Marker:
        pass

    m = Marker()
    captured: list[object] = []

    def body(x: object) -> object:
        captured.append(x)
        return none

    adapter = bridge(Block(body))
    adapter(m)
    assert captured[0] is m


# --- Boolean handled before Int (bool is a subclass of int) ---


def test_to_poop_bool_not_misclassified_as_int() -> None:
    assert to_poop(True) is true
    assert isinstance(to_poop(True), Boolean)


def test_to_python_NoneClass_instance() -> None:
    assert to_python(NoneClass()) is None
