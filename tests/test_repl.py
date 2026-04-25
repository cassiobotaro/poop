import sys

import pytest

from poop.errors import ExecutionError, ParseError, ValidationError
from poop.interpreter import Interpreter
from poop.repl import (
    Repl,
    _color,
    _colorize_value,
    _indent_for,
    _PoopCompleter,
    _save_history,
    _setup_readline,
)
from poop.transformers import DEFAULT_NAMESPACE


def _repl() -> tuple[Repl, dict[str, object]]:
    interp = Interpreter()
    repl = Repl(interp)
    return repl, repl._ns


def test_namespace_persists_across_calls() -> None:
    from poop.types.int import Int

    repl, ns = _repl()
    repl._interpreter.run_source_repl("x = 42", ns)
    repl._interpreter.run_source_repl("y = x + 1", ns)
    assert ns["y"] == Int(43)


def test_repl_initial_namespace_contains_poop_bindings() -> None:
    _, ns = _repl()
    assert "_poop_true" in ns
    assert "_poop_false" in ns
    assert "_poop_int" in ns


def test_parse_error_does_not_kill_repl_namespace() -> None:
    repl, ns = _repl()
    repl._interpreter.run_source_repl("x = 1", ns)
    with pytest.raises(ParseError):
        repl._interpreter.run_source_repl("def :", ns)
    assert "x" in ns


def test_validation_error_does_not_kill_repl_namespace() -> None:
    repl, ns = _repl()
    repl._interpreter.run_source_repl("x = 1", ns)
    with pytest.raises(ValidationError):
        repl._interpreter.run_source_repl("if True:\n    pass", ns)
    assert "x" in ns


def test_execution_error_does_not_kill_repl_namespace() -> None:
    repl, ns = _repl()
    repl._interpreter.run_source_repl("x = 1", ns)
    with pytest.raises(ExecutionError):
        repl._interpreter.run_source_repl("y = 1 / 0", ns)
    assert "x" in ns
    assert "y" not in ns


def test_repl_namespace_is_independent_of_default_namespace() -> None:
    repl, ns = _repl()
    repl._interpreter.run_source_repl("sentinel_var = 99", ns)
    assert "sentinel_var" not in DEFAULT_NAMESPACE


# --- _indent_for ---


def test_indent_for_empty_buffer() -> None:
    assert _indent_for([]) == ""


def test_indent_for_plain_line_no_indent() -> None:
    assert _indent_for(["x = 1"]) == ""


def test_indent_for_colon_adds_four_spaces() -> None:
    assert _indent_for(["class Foo:"]) == "    "


def test_indent_for_nested_colon_adds_four_more() -> None:
    assert _indent_for(["    def m(self):"]) == "        "


def test_indent_for_indented_non_colon_preserves_indent() -> None:
    assert _indent_for(["    x = 1"]) == "    "


def test_indent_for_colon_with_trailing_whitespace() -> None:
    assert _indent_for(["class Foo:   "]) == "    "


def test_indent_for_uses_only_last_buffer_line() -> None:
    assert _indent_for(["class Foo:", "    pass"]) == "    "


# --- _setup_readline ---


def test_setup_readline_does_not_crash() -> None:
    _setup_readline({})


def test_setup_readline_with_nonempty_namespace_does_not_crash() -> None:
    _setup_readline({"x": 1, "_poop_true": True})


# --- _save_history ---


def test_save_history_does_not_crash() -> None:
    _save_history()


# --- _displayhook ---


def test_displayhook_stores_value_in_namespace(
    capsys: pytest.CaptureFixture[str],
) -> None:
    repl, ns = _repl()
    repl._displayhook(42)
    assert ns["_"] == 42


def test_displayhook_none_is_not_stored(capsys: pytest.CaptureFixture[str]) -> None:
    repl, ns = _repl()
    repl._displayhook(42)
    repl._displayhook(None)
    assert ns["_"] == 42


def test_displayhook_prints_repr(capsys: pytest.CaptureFixture[str]) -> None:
    repl, _ = _repl()
    repl._displayhook("hello")
    assert "'hello'" in capsys.readouterr().out


def test_displayhook_none_prints_nothing(capsys: pytest.CaptureFixture[str]) -> None:
    repl, _ = _repl()
    repl._displayhook(None)
    assert capsys.readouterr().out == ""


# --- run() integration ---


def _fake_input(*responses: object) -> object:
    """Returns a function that yields responses, raising exceptions when given one."""

    def _input(_prompt: str) -> str:
        val = next(it)
        if isinstance(val, BaseException):
            raise val
        return str(val)

    it = iter(responses)
    return _input


def test_run_exits_on_eof(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("builtins.input", _fake_input(EOFError()))
    Repl(Interpreter()).run()


def test_run_ctrl_c_clears_buffer_and_continues(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("builtins.input", _fake_input(KeyboardInterrupt(), EOFError()))
    Repl(Interpreter()).run()


def test_run_restores_displayhook_after_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    original = sys.displayhook
    monkeypatch.setattr("builtins.input", _fake_input(EOFError()))
    Repl(Interpreter()).run()
    assert sys.displayhook is original


def test_run_restores_displayhook_on_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    original = sys.displayhook

    def _bad_input(_prompt: str) -> str:
        raise RuntimeError("unexpected")

    monkeypatch.setattr("builtins.input", _bad_input)
    with pytest.raises(RuntimeError):
        Repl(Interpreter()).run()
    assert sys.displayhook is original


def test_run_stores_last_result_in_underscore(monkeypatch: pytest.MonkeyPatch) -> None:
    from poop.types.int import Int

    repl = Repl(Interpreter())
    monkeypatch.setattr("builtins.input", _fake_input("1 + 1", EOFError()))
    repl.run()
    assert repl._ns.get("_") == Int(2)


def test_run_poop_error_printed_to_stderr(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        "builtins.input", _fake_input("if True:\n    pass\n", "", EOFError())
    )
    Repl(Interpreter()).run()
    assert "poop:" in capsys.readouterr().err


# --- _PoopCompleter ---


def test_poop_completer_name_matches_user_vars() -> None:
    ns: dict[str, object] = {"foo": 1, "bar": 2}
    c = _PoopCompleter(ns)
    assert c.complete("fo", 0) == "foo"
    assert c.complete("fo", 1) is None


def test_poop_completer_hides_poop_internals() -> None:
    ns: dict[str, object] = {"_poop_true": True, "x": 1}
    c = _PoopCompleter(ns)
    assert c.complete("_poop", 0) is None


def test_poop_completer_no_builtins_leak() -> None:
    ns: dict[str, object] = {}
    c = _PoopCompleter(ns)
    assert c.complete("pri", 0) is None
    assert c.complete("len", 0) is None


def test_poop_completer_callable_gets_paren() -> None:
    ns: dict[str, object] = {"my_fn": lambda: None}
    c = _PoopCompleter(ns)
    assert c.complete("my", 0) == "my_fn("


def test_poop_completer_attr_matches() -> None:
    from poop.types.int import Int

    ns: dict[str, object] = {"n": Int(1)}
    c = _PoopCompleter(ns)
    result = c.complete("n.ab", 0)
    assert result == "n.abs("


def test_poop_completer_attr_hides_dunder() -> None:
    from poop.types.int import Int

    ns: dict[str, object] = {"n": Int(1)}
    c = _PoopCompleter(ns)
    assert c.complete("n.__", 0) is None


def test_poop_completer_attr_bad_expr_returns_none() -> None:
    ns: dict[str, object] = {}
    c = _PoopCompleter(ns)
    assert c.complete("nonexistent.foo", 0) is None


# --- _colorize_value ---


def test_colorize_value_no_color_when_not_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)
    from poop.types.int import Int

    assert _colorize_value(Int(1)) == "1"


def test_colorize_value_int_contains_ansi_when_tty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    from poop.types.int import Int

    result = _colorize_value(Int(1))
    assert "\x1b[" in result
    assert "1" in result


def test_colorize_value_str_uses_quoted_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    from poop.types.string import Str

    result = _colorize_value(Str("hello"))
    assert "'hello'" in result


def test_color_no_ansi_when_not_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdout.isatty", lambda: False)
    assert _color("text", "\x1b[31m") == "text"


def test_color_wraps_ansi_when_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdout.isatty", lambda: True)
    result = _color("text", "\x1b[31m")
    assert result.startswith("\x1b[31m")
    assert "text" in result
