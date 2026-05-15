import pathlib

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tomllib import Tomllib


def test_loads_simple_table() -> None:
    result = Tomllib.loads(Str('name = "alice"\nage = 30'))
    assert isinstance(result, Dict)
    assert result.at(Str("name")) == Str("alice")
    assert result.at(Str("age")) == Int(30)


def test_loads_nested_table() -> None:
    result = Tomllib.loads(Str('[server]\nhost = "localhost"\nport = 8080'))
    server = result.at(Str("server"))
    assert isinstance(server, Dict)
    assert server.at(Str("port")) == Int(8080)


def test_loads_array() -> None:
    result = Tomllib.loads(Str("nums = [1, 2, 3]"))
    nums = result.at(Str("nums"))
    assert isinstance(nums, List)
    assert nums == List(Int(1), Int(2), Int(3))


def test_loads_float() -> None:
    result = Tomllib.loads(Str("pi = 3.14"))
    assert isinstance(result.at(Str("pi")), Float)


def test_loads_booleans() -> None:
    result = Tomllib.loads(Str("a = true\nb = false"))
    assert result.at(Str("a")) is true
    assert result.at(Str("b")) is false


def test_loads_date_flattened_to_iso_str() -> None:
    result = Tomllib.loads(Str("d = 2026-05-15"))
    d = result.at(Str("d"))
    assert isinstance(d, Str)
    assert d._value == "2026-05-15"


def test_loads_invalid_raises_decode_error() -> None:
    with pytest.raises(Tomllib.TOMLDecodeError):
        Tomllib.loads(Str("invalid = [unclosed"))


def test_load_from_path(tmp_path: pathlib.Path) -> None:
    toml_file = tmp_path / "config.toml"
    toml_file.write_text('name = "alice"\n[nested]\nkey = "value"')
    result = Tomllib.load(Path(Str(str(toml_file))))
    assert isinstance(result, Dict)
    assert result.at(Str("name")) == Str("alice")
    nested = result.at(Str("nested"))
    assert isinstance(nested, Dict)
    assert nested.at(Str("key")) == Str("value")


def test_tomllib_reachable_via_interpreter() -> None:
    Interpreter().run_source('tomllib.loads("k = 1").at("k").print()')
