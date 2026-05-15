import webbrowser as _webbrowser
from unittest import mock

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import Boolean, false, true
from poop.types.int import Int
from poop.types.string import Str
from poop.types.webbrowser import Browser, Webbrowser

# --- Module-level open ---


def test_open_returns_poop_boolean() -> None:
    with mock.patch("poop.types.webbrowser._webbrowser.open", return_value=True):
        result = Webbrowser.open(Str("https://example.com"))
    assert isinstance(result, Boolean)
    assert result is true


def test_open_false_when_underlying_returns_false() -> None:
    with mock.patch("poop.types.webbrowser._webbrowser.open", return_value=False):
        result = Webbrowser.open(Str("https://example.com"))
    assert result is false


def test_open_passes_default_kwargs() -> None:
    with mock.patch(
        "poop.types.webbrowser._webbrowser.open", return_value=True
    ) as patched:
        Webbrowser.open(Str("https://example.com"))
    patched.assert_called_once_with("https://example.com", new=0, autoraise=True)


def test_open_passes_custom_kwargs() -> None:
    with mock.patch(
        "poop.types.webbrowser._webbrowser.open", return_value=True
    ) as patched:
        Webbrowser.open(Str("https://example.com"), Int(2), false)
    patched.assert_called_once_with("https://example.com", new=2, autoraise=False)


def test_open_new_returns_poop_boolean() -> None:
    with mock.patch(
        "poop.types.webbrowser._webbrowser.open_new", return_value=True
    ) as patched:
        result = Webbrowser.open_new(Str("https://example.com"))
    assert result is true
    patched.assert_called_once_with("https://example.com")


def test_open_new_tab_returns_poop_boolean() -> None:
    with mock.patch(
        "poop.types.webbrowser._webbrowser.open_new_tab", return_value=True
    ) as patched:
        result = Webbrowser.open_new_tab(Str("https://example.com"))
    assert result is true
    patched.assert_called_once_with("https://example.com")


# --- get ---


def test_get_returns_browser() -> None:
    browser = Webbrowser.get()
    assert isinstance(browser, Browser)


def test_get_with_using_argument_forwards() -> None:
    with mock.patch("poop.types.webbrowser._webbrowser.get") as patched:
        patched.return_value = _webbrowser.GenericBrowser("/usr/bin/echo")
        Webbrowser.get(Str("xdg-open"))
    patched.assert_called_once_with("xdg-open")


def test_get_invalid_using_raises_error() -> None:
    with pytest.raises(Webbrowser.Error):
        Webbrowser.get(Str("definitely-not-a-real-browser-poop-test"))


# --- Browser instance ---


def test_browser_open_returns_poop_boolean() -> None:
    fake_impl = mock.Mock(spec=_webbrowser.BaseBrowser)
    fake_impl.open.return_value = True
    fake_impl.name = "fake"
    browser = Browser(fake_impl)
    result = browser.open(Str("https://example.com"))
    assert result is true
    fake_impl.open.assert_called_once_with("https://example.com", new=0, autoraise=True)


def test_browser_name_property() -> None:
    fake_impl = mock.Mock(spec=_webbrowser.BaseBrowser)
    fake_impl.name = "chrome"
    browser = Browser(fake_impl)
    assert browser.name == Str("chrome")


def test_browser_open_new() -> None:
    fake_impl = mock.Mock(spec=_webbrowser.BaseBrowser)
    fake_impl.open_new.return_value = True
    fake_impl.name = "fake"
    browser = Browser(fake_impl)
    assert browser.open_new(Str("https://example.com")) is true


def test_browser_open_new_tab() -> None:
    fake_impl = mock.Mock(spec=_webbrowser.BaseBrowser)
    fake_impl.open_new_tab.return_value = True
    fake_impl.name = "fake"
    browser = Browser(fake_impl)
    assert browser.open_new_tab(Str("https://example.com")) is true


def test_browser_str_includes_name() -> None:
    fake_impl = mock.Mock(spec=_webbrowser.BaseBrowser)
    fake_impl.name = "fake"
    browser = Browser(fake_impl)
    assert "fake" in str(browser)


# --- Error class ---


def test_error_is_python_exception_class() -> None:
    assert Webbrowser.Error is _webbrowser.Error
    assert issubclass(Webbrowser.Error, Exception)


# --- Interpreter integration ---


def test_webbrowser_reachable_via_interpreter() -> None:
    with mock.patch("poop.types.webbrowser._webbrowser.open", return_value=True):
        Interpreter().run_source('webbrowser.open("https://example.com").print()')


def test_Browser_in_default_namespace() -> None:
    from poop.transformers import DEFAULT_NAMESPACE

    assert DEFAULT_NAMESPACE["Browser"] is Browser
