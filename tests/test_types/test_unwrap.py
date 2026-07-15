from poop.types._unwrap import _is_absent, _unwrap, _unwrap_bool
from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.string import Str


def test_is_absent_for_python_none() -> None:
    assert _is_absent(None) is True


def test_is_absent_for_poop_none() -> None:
    assert _is_absent(none) is True


def test_is_absent_for_present_value() -> None:
    assert _is_absent(Int(0)) is False
    assert _is_absent(false) is False
    assert _is_absent(Str("")) is False


def test_unwrap_returns_default_for_python_none() -> None:
    assert _unwrap(None, "fallback") == "fallback"


def test_unwrap_returns_default_for_poop_none() -> None:
    assert _unwrap(none, "fallback") == "fallback"


def test_unwrap_returns_inner_value() -> None:
    assert _unwrap(Int(7), "fallback") == 7
    assert _unwrap(Str("hi"), "fallback") == "hi"


def test_unwrap_bool_returns_default_for_python_none() -> None:
    assert _unwrap_bool(None, True) is True


def test_unwrap_bool_returns_default_for_poop_none() -> None:
    assert _unwrap_bool(none, True) is True


def test_unwrap_bool_coerces_present_value() -> None:
    assert _unwrap_bool(true, False) is True
    assert _unwrap_bool(false, True) is False


def test_unwrap_accepts_nested_none_class_instance() -> None:
    custom_none = NoneClass()
    assert _is_absent(custom_none) is True
    assert _unwrap(custom_none, 42) == 42
