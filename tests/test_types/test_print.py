import pytest

from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_object_print_outputs_str(capsys: pytest.CaptureFixture[str]) -> None:
    Int(42).print()
    assert capsys.readouterr().out == "42\n"


def test_object_print_returns_none() -> None:
    assert Int(1).print() is none


def test_object_print_end_param(capsys: pytest.CaptureFixture[str]) -> None:
    Int(42).print(end="")
    assert capsys.readouterr().out == "42"


def test_str_print(capsys: pytest.CaptureFixture[str]) -> None:
    Str("hello").print()
    assert capsys.readouterr().out == "hello\n"


def test_empty_str_print_blank_line(capsys: pytest.CaptureFixture[str]) -> None:
    Str("").print()
    assert capsys.readouterr().out == "\n"


def test_list_print_default_sep(capsys: pytest.CaptureFixture[str]) -> None:
    List(Int(1), Int(2), Int(3)).print()
    assert capsys.readouterr().out == "1 2 3\n"


def test_list_print_custom_sep(capsys: pytest.CaptureFixture[str]) -> None:
    List(Int(1), Int(2), Int(3)).print(sep=";")
    assert capsys.readouterr().out == "1;2;3\n"


def test_list_print_returns_none() -> None:
    assert List(Int(1)).print() is none


def test_tuple_print_default_sep(capsys: pytest.CaptureFixture[str]) -> None:
    Tuple(Int(1), Int(2), Int(3)).print()
    assert capsys.readouterr().out == "1 2 3\n"


def test_tuple_print_custom_sep(capsys: pytest.CaptureFixture[str]) -> None:
    Tuple(Int(1), Int(2), Int(3)).print(sep=", ")
    assert capsys.readouterr().out == "1, 2, 3\n"


def test_tuple_print_returns_none() -> None:
    assert Tuple(Int(1)).print() is none
