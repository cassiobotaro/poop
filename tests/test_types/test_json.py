import pathlib

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import Boolean, false, true
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.json import Json
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.path import Path
from poop.types.string import Str

# --- dumps ---


def test_dumps_dict_returns_poop_str() -> None:
    d = Dict().at_put(Str("a"), Int(1)).at_put(Str("b"), Int(2))
    result = Json.dumps(d)
    assert isinstance(result, Str)
    assert '"a"' in result._value and "1" in result._value


def test_dumps_list_of_ints() -> None:
    result = Json.dumps(List(Int(1), Int(2), Int(3)))
    assert result == Str("[1, 2, 3]")


def test_dumps_str() -> None:
    result = Json.dumps(Str("hello"))
    assert result == Str('"hello"')


def test_dumps_bool_true() -> None:
    assert Json.dumps(true) == Str("true")


def test_dumps_bool_false() -> None:
    assert Json.dumps(false) == Str("false")


def test_dumps_none() -> None:
    assert Json.dumps(none) == Str("null")


def test_dumps_nested() -> None:
    obj = Dict().at_put(Str("nums"), List(Int(1), Int(2)))
    result = Json.dumps(obj)
    assert isinstance(result, Str)
    assert "nums" in result._value


def test_dumps_indent() -> None:
    obj = Dict().at_put(Str("a"), Int(1))
    result = Json.dumps(obj, indent=Int(2))
    assert "\n" in result._value


def test_dumps_sort_keys() -> None:
    obj = Dict().at_put(Str("b"), Int(2)).at_put(Str("a"), Int(1))
    result = Json.dumps(obj, sort_keys=true)
    # Sorted: "a" before "b"
    assert result._value.index('"a"') < result._value.index('"b"')


# --- loads ---


def test_loads_dict_returns_poop_dict() -> None:
    result = Json.loads(Str('{"a": 1, "b": 2}'))
    assert isinstance(result, Dict)
    assert result.at(Str("a")) == Int(1)
    assert result.at(Str("b")) == Int(2)


def test_loads_list_returns_poop_list() -> None:
    result = Json.loads(Str("[1, 2, 3]"))
    assert isinstance(result, List)
    assert result == List(Int(1), Int(2), Int(3))


def test_loads_str_returns_poop_str() -> None:
    assert Json.loads(Str('"hello"')) == Str("hello")


def test_loads_int_returns_poop_int() -> None:
    result = Json.loads(Str("42"))
    assert isinstance(result, Int)
    assert result == Int(42)


def test_loads_float_returns_poop_float() -> None:
    result = Json.loads(Str("3.14"))
    assert isinstance(result, Float)


def test_loads_true_returns_poop_true() -> None:
    result = Json.loads(Str("true"))
    assert isinstance(result, Boolean)
    assert result is true


def test_loads_false_returns_poop_false() -> None:
    assert Json.loads(Str("false")) is false


def test_loads_null_returns_poop_none() -> None:
    assert Json.loads(Str("null")) is none


def test_loads_invalid_raises_decode_error() -> None:
    with pytest.raises(Json.JSONDecodeError):
        Json.loads(Str("{invalid"))


def test_loads_nested_round_trip() -> None:
    original = Str('{"name": "alice", "ages": [10, 20, 30]}')
    result = Json.loads(original)
    assert isinstance(result, Dict)
    assert result.at(Str("name")) == Str("alice")
    ages = result.at(Str("ages"))
    assert isinstance(ages, List)
    assert ages == List(Int(10), Int(20), Int(30))


# --- dump / load (path-based) ---


def test_dump_writes_file_and_load_round_trips(tmp_path: pathlib.Path) -> None:
    path = Path(Str(str(tmp_path / "data.json")))
    obj = Dict().at_put(Str("k"), Int(42))
    result = Json.dump(obj, path)
    assert result is none
    loaded = Json.load(path)
    assert isinstance(loaded, Dict)
    assert loaded.at(Str("k")) == Int(42)


def test_dump_with_indent(tmp_path: pathlib.Path) -> None:
    path = Path(Str(str(tmp_path / "indented.json")))
    Json.dump(Dict().at_put(Str("a"), Int(1)), path, indent=Int(2))
    content = path.read_text()
    assert "\n" in content._value


# --- Interpreter integration ---


def test_json_loads_reachable_via_interpreter() -> None:
    Interpreter().run_source('json.loads(\'{"a": 1}\').at("a").print()')


def test_json_dumps_reachable_via_interpreter() -> None:
    Interpreter().run_source("json.dumps([1, 2, 3]).print()")


# --- Round-trip discipline ---


def test_round_trip_preserves_types() -> None:
    original = Dict()
    original.at_put(Str("name"), Str("alice"))
    original.at_put(Str("age"), Int(30))
    original.at_put(Str("score"), Float(95.5))
    original.at_put(Str("admin"), true)
    original.at_put(Str("note"), none)
    original.at_put(Str("tags"), List(Str("a"), Str("b")))

    encoded = Json.dumps(original)
    decoded = Json.loads(encoded)
    assert isinstance(decoded, Dict)
    assert isinstance(decoded.at(Str("name")), Str)
    assert isinstance(decoded.at(Str("age")), Int)
    assert isinstance(decoded.at(Str("score")), Float)
    assert isinstance(decoded.at(Str("admin")), Boolean)
    assert isinstance(decoded.at(Str("note")), NoneClass)
    assert isinstance(decoded.at(Str("tags")), List)


# --- Try.except_ integration ---


def test_try_catches_json_decode_error() -> None:
    from poop.types.try_ import Try

    captured: list[object] = []
    Try(lambda: Json.loads(Str("{invalid"))).except_(
        Json.JSONDecodeError, lambda e: captured.append(e.message())
    ).run()
    assert len(captured) == 1
    assert isinstance(captured[0], Str)
