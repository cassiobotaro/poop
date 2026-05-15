from unittest import mock

from poop.interpreter import Interpreter
from poop.types.getpass import Getpass
from poop.types.none import none
from poop.types.string import Str


def test_getuser_returns_poop_str() -> None:
    result = Getpass.getuser()
    assert isinstance(result, Str)


def test_getuser_matches_underlying_module() -> None:
    import getpass as _getpass

    assert Getpass.getuser()._value == _getpass.getuser()


def test_getpass_returns_poop_str() -> None:
    with mock.patch("poop.types.getpass._getpass.getpass", return_value="hunter2"):
        result = Getpass.getpass()
    assert isinstance(result, Str)
    assert result._value == "hunter2"


def test_getpass_default_prompt() -> None:
    with mock.patch("poop.types.getpass._getpass.getpass", return_value="") as patched:
        Getpass.getpass()
    patched.assert_called_once_with("Password: ")


def test_getpass_custom_prompt() -> None:
    with mock.patch("poop.types.getpass._getpass.getpass", return_value="") as patched:
        Getpass.getpass(Str("PIN: "))
    patched.assert_called_once_with("PIN: ")


def test_getpass_explicit_none_stream() -> None:
    with mock.patch("poop.types.getpass._getpass.getpass", return_value="") as patched:
        Getpass.getpass(Str("PIN: "), none)
    patched.assert_called_once_with("PIN: ")


def test_getpass_reachable_via_interpreter() -> None:
    with mock.patch("poop.types.getpass._getpass.getuser", return_value="alice"):
        Interpreter().run_source("getpass.getuser().print()")
