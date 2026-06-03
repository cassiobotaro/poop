import pathlib

import pytest

from poop.interpreter import Interpreter
from poop.types.block import Block
from poop.types.boolean import false, true
from poop.types.datetime import Date, DateTime, Time
from poop.types.decimal import Decimal
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


def test_loads_local_date_returns_poop_date() -> None:
    result = Tomllib.loads(Str("d = 2026-05-15"))
    d = result.at(Str("d"))
    assert isinstance(d, Date)
    assert d == Date(Int(2026), Int(5), Int(15))


def test_loads_local_time_returns_poop_time() -> None:
    result = Tomllib.loads(Str("t = 09:30:00"))
    t = result.at(Str("t"))
    assert isinstance(t, Time)
    assert t == Time(Int(9), Int(30), Int(0))


def test_loads_local_datetime_returns_poop_datetime() -> None:
    result = Tomllib.loads(Str("ts = 2026-05-15T09:30:00"))
    ts = result.at(Str("ts"))
    assert isinstance(ts, DateTime)


def test_loads_offset_datetime_returns_poop_datetime() -> None:
    result = Tomllib.loads(Str("ts = 2026-05-15T09:30:00Z"))
    ts = result.at(Str("ts"))
    assert isinstance(ts, DateTime)


def test_loads_date_nested_in_array_returns_poop_date() -> None:
    # Datetimes nested inside arrays must still wrap to POOP types: the
    # recursion runs through _wrap, since to_poop has no datetime branch.
    result = Tomllib.loads(Str("dates = [2026-05-15, 2026-05-16]"))
    arr = result.at(Str("dates"))
    assert isinstance(arr, List)
    first = arr.at(Int(0))
    assert isinstance(first, Date)
    assert first == Date(Int(2026), Int(5), Int(15))


def test_loads_datetime_nested_in_table_returns_poop_datetime() -> None:
    result = Tomllib.loads(Str("[event]\nwhen = 2026-05-15T09:30:00"))
    table = result.at(Str("event"))
    assert isinstance(table, Dict)
    assert isinstance(table.at(Str("when")), DateTime)


def test_loads_parse_float_bridged_to_decimal() -> None:
    captured: list[Str] = []

    def to_decimal(s: Str) -> Decimal:
        captured.append(s)
        return Decimal(s)

    result = Tomllib.loads(
        Str("pi = 3.14"),
        parse_float=Block(to_decimal),
    )
    pi = result.at(Str("pi"))
    assert isinstance(pi, Decimal)
    assert captured == [Str("3.14")]


def test_loads_parse_float_default_is_python_float() -> None:
    # Default mirrors CPython: stays as Python float, wrapped to POOP Float.
    result = Tomllib.loads(Str("pi = 3.14"))
    assert isinstance(result.at(Str("pi")), Float)


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
