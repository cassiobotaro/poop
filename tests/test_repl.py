import ast
import io
import sys

import pytest
from rich.console import Console

import poop.validators as validators
from poop.errors import ExecutionError, ParseError, ValidationError
from poop.interpreter import Interpreter
from poop.repl import (
    _CYAN,
    _EXPLAIN_CALLS,
    _EXPLAIN_SNIPPETS,
    Repl,
    _error,
    _explain_snippet,
    _indent_for,
    _PoopCompleter,
    _print_error,
    _print_value,
    _rl_color,
    _save_history,
    _setup_readline,
    _value_text,
)
from poop.transformers import DEFAULT_NAMESPACE
from poop.types.int import Int
from poop.types.string import Str
from poop.validators import DEFAULT_VALIDATORS


def _repl() -> tuple[Repl, dict[str, object]]:
    interp = Interpreter()
    repl = Repl(interp)
    return repl, repl._ns


def test_namespace_persists_across_calls() -> None:
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


def test_displayhook_poop_none_prints_nothing(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # proposal 125: `.print()` answers POOP none, which must not echo.
    from poop.types.none import none

    repl, _ = _repl()
    repl._displayhook(none)
    assert capsys.readouterr().out == ""


def test_displayhook_poop_none_does_not_clobber_underscore(
    capsys: pytest.CaptureFixture[str],
) -> None:
    from poop.types.none import none

    repl, ns = _repl()
    repl._displayhook(Int(7))
    repl._displayhook(none)
    assert ns["_"] == Int(7)


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


def test_run_poop_error_shows_the_source_line_and_caret(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # The REPL holds the source; it used to cite a line that had scrolled away.
    monkeypatch.setattr("builtins.input", _fake_input("print(x)", EOFError()))
    Repl(Interpreter()).run()
    err = capsys.readouterr().err
    assert "  1 | print(x)" in err
    assert "    | ^" in err


def test_run_poop_error_does_not_repeat_the_position(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("builtins.input", _fake_input("print(x)", EOFError()))
    Repl(Interpreter()).run()
    assert "(line 1, col 0)" not in capsys.readouterr().err


def test_run_runtime_error_shows_the_source_line(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("builtins.input", _fake_input("1 / 0", EOFError()))
    Repl(Interpreter()).run()
    err = capsys.readouterr().err
    assert "ZeroDivisionError" in err
    assert "  1 | 1 / 0" in err


def test_run_error_line_refers_to_the_current_input_not_an_earlier_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # A method defined in one input raises when called from a later, multi-line
    # input. The deepest traceback frame is the method's `raise`, whose line
    # counts against the *earlier* buffer — citing it against the current one
    # pointed the gutter at an unrelated line. The cited line must be the call
    # site in the current buffer (line 3), never the stale line 2.
    monkeypatch.setattr(
        "builtins.input",
        _fake_input(
            "class Foo:",
            "    def bar(self): ValueError.raise_('boom')",
            "",
            "x = (",
            "    99",
            "    + Foo().bar()",
            ")",
            EOFError(),
        ),
    )
    Repl(Interpreter()).run()
    err = capsys.readouterr().err
    assert "ValueError: boom" in err
    assert "  3 |     + Foo().bar()" in err
    assert "  2 |     99" not in err


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
    ns: dict[str, object] = {"n": Int(1)}
    c = _PoopCompleter(ns)
    result = c.complete("n.ab", 0)
    assert result == "n.abs("


def test_poop_completer_attr_hides_dunder() -> None:
    ns: dict[str, object] = {"n": Int(1)}
    c = _PoopCompleter(ns)
    assert c.complete("n.__", 0) is None


def test_poop_completer_attr_hides_every_private_name() -> None:
    # The completer filtered `__`-prefixed names only, so Tab offered
    # `x._value` — the raw Python value `_reject_private` exists to keep out of
    # user code — plus `_abc_impl` and `_eq_group`, POOP internals with no
    # meaning in the language. `dir()` and `:methods` never showed them.
    c = _PoopCompleter({"x": Str("abc")})
    assert c._attr_matches("x._") == []
    assert c.complete("x._val", 0) is None


def test_poop_completer_name_hides_every_private_binding() -> None:
    # `_poop_`-prefixed was the old filter; any other `_` key is machinery too.
    c = _PoopCompleter({"_poop_true": True, "_secret": 1, "x": 1})
    assert c._name_matches("_") == []


def test_poop_completer_does_not_run_a_property() -> None:
    # Deciding whether to append `(` used to read the attribute off the
    # *instance*, which runs a `property` getter: pressing Tab executed
    # program code.
    calls: list[str] = []

    class WithProperty:
        @property
        def trap(self) -> str:
            calls.append("ran")
            return "value"

    c = _PoopCompleter({"obj": WithProperty()})
    assert c._attr_matches("obj.tra") == ["obj.trap"]
    assert calls == []


def test_poop_completer_attr_bad_expr_returns_none() -> None:
    ns: dict[str, object] = {}
    c = _PoopCompleter(ns)
    assert c.complete("nonexistent.foo", 0) is None


def test_poop_completer_attr_does_not_call_function() -> None:
    calls: list[str] = []

    def danger() -> str:
        calls.append("called")
        return "value"

    ns: dict[str, object] = {"danger": danger}
    c = _PoopCompleter(ns)
    assert c.complete("danger().up", 0) is None
    assert calls == []


def test_poop_completer_attr_rejects_walrus() -> None:
    ns: dict[str, object] = {}
    c = _PoopCompleter(ns)
    assert c.complete("(x := 1).bit_l", 0) is None
    assert "x" not in ns


def test_poop_completer_attr_rejects_subscript() -> None:
    ns: dict[str, object] = {"lst": [Int(1)]}
    c = _PoopCompleter(ns)
    assert c.complete("lst[0].ab", 0) is None


def test_poop_completer_attr_allows_literal() -> None:
    ns: dict[str, object] = {}
    c = _PoopCompleter(ns)
    assert c.complete("'hi'.upp", 0) == "'hi'.upper("


# --- colorized output (rich, one console per stream) ---


def _console(buf: io.StringIO, *, terminal: bool) -> Console:
    return Console(
        file=buf,
        force_terminal=terminal,
        color_system="standard",
        no_color=not terminal,
    )


def test_value_text_int_is_yellow() -> None:
    text = _value_text(Int(1))
    assert text.plain == "1"
    assert text.style == "yellow"


def test_value_text_str_uses_quoted_repr() -> None:
    text = _value_text(Str("hello"))
    assert text.plain == "'hello'"
    assert text.style == "green"


def test_value_text_bool_is_blue() -> None:
    from poop.types.boolean import true

    assert _value_text(true).style == "blue"


def test_value_text_other_is_unstyled() -> None:
    assert _value_text(object()).style == ""


def test_print_value_emits_ansi_on_a_terminal(monkeypatch: pytest.MonkeyPatch) -> None:
    buf = io.StringIO()
    monkeypatch.setattr("poop.repl._OUT", _console(buf, terminal=True))
    _print_value(Int(1))
    out = buf.getvalue()
    assert "\x1b[" in out
    assert "1" in out


def test_print_value_plain_when_not_a_terminal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    buf = io.StringIO()
    monkeypatch.setattr("poop.repl._OUT", _console(buf, terminal=False))
    _print_value(Int(1))
    assert buf.getvalue() == "1\n"


def test_diagnostics_and_values_colorize_per_stream(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # `poop 2>err.log`: stdout a tty, stderr a file. The value echo colorizes
    # off stdout while the diagnostic must not leak ANSI into redirected stderr.
    out_buf, err_buf = io.StringIO(), io.StringIO()
    monkeypatch.setattr("poop.repl._OUT", _console(out_buf, terminal=True))
    monkeypatch.setattr("poop.repl._ERR", _console(err_buf, terminal=False))
    _print_value(Int(1))
    _error("boom")
    assert "\x1b[" in out_buf.getvalue()
    assert err_buf.getvalue() == "poop: boom\n"


def test_diagnostic_colorizes_when_only_stderr_is_a_terminal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The reverse (`poop >out.txt`): stderr a tty, stdout a file. The
    # diagnostic must still colorize off stderr.
    err_buf = io.StringIO()
    monkeypatch.setattr("poop.repl._OUT", _console(io.StringIO(), terminal=False))
    monkeypatch.setattr("poop.repl._ERR", _console(err_buf, terminal=True))
    _error("boom")
    out = err_buf.getvalue()
    assert "\x1b[" in out
    assert "poop: boom" in out


def test_print_error_keeps_the_caret_aligned_and_plain_off_a_terminal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    buf = io.StringIO()
    monkeypatch.setattr("poop.repl._ERR", _console(buf, terminal=False))
    _print_error(ValidationError("if is forbidden", 1, 0), "if x:")
    out = buf.getvalue()
    assert "\x1b[" not in out
    assert "  1 | if x:" in out
    assert "    | ^" in out


def test_print_error_syntax_highlights_the_line_on_a_terminal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    buf = io.StringIO()
    monkeypatch.setattr("poop.repl._ERR", _console(buf, terminal=True))
    _print_error(ValidationError("if is forbidden", 1, 0), "if x:")
    out = buf.getvalue()
    assert "\x1b[" in out  # coloured
    assert "poop: if is forbidden" in out  # the message survives intact
    # the offending line is quoted, but the highlighter splits its tokens with
    # ANSI codes, so assert on the tokens rather than the contiguous line.
    assert "if" in out
    assert "x:" in out
    assert "^" in out  # caret preserved


def test_rl_color_plain_when_not_a_terminal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("poop.repl._OUT", _console(io.StringIO(), terminal=False))
    assert _rl_color(">>>", _CYAN) == ">>>"


def test_rl_color_wraps_with_readline_markers_on_a_terminal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("poop.repl._OUT", _console(io.StringIO(), terminal=True))
    result = _rl_color(">>>", _CYAN)
    assert result.startswith("\001")
    assert _CYAN in result
    assert ">>>" in result


# --- meta-commands ---


def test_meta_methods_lists_messages(capsys: pytest.CaptureFixture[str]) -> None:
    repl, _ = _repl()
    repl._meta(':methods "abc"')
    out = capsys.readouterr().out
    assert "upper" in out
    assert "understands" in out


def test_meta_methods_literal_answers_poop_messages(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The literal must go through the pipeline: "abc" is a POOP Str,
    # not a Python str — it answers at/print/class_name.
    repl, _ = _repl()
    repl._meta(':methods "abc"')
    out = capsys.readouterr().out
    assert "class_name" in out
    assert "print" in out


def test_meta_methods_hides_underscored_names(
    capsys: pytest.CaptureFixture[str],
) -> None:
    repl, _ = _repl()
    repl._meta(':methods "abc"')
    out = capsys.readouterr().out
    assert "__init__" not in out
    assert "_value" not in out


def test_meta_methods_works_on_namespace_variable(
    capsys: pytest.CaptureFixture[str],
) -> None:
    repl, ns = _repl()
    repl._interpreter.run_source_repl("nums = [1, 2]", ns)
    repl._meta(":methods nums")
    out = capsys.readouterr().out
    assert "append" in out


def test_meta_methods_without_arg_shows_usage(
    capsys: pytest.CaptureFixture[str],
) -> None:
    repl, _ = _repl()
    repl._meta(":methods")
    assert "usage" in capsys.readouterr().out


def test_meta_methods_rejects_calls(capsys: pytest.CaptureFixture[str]) -> None:
    repl, _ = _repl()
    repl._meta(":methods danger()")
    err = capsys.readouterr().err
    assert "calls are not evaluated" in err


def test_meta_methods_unknown_name_reports_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    repl, _ = _repl()
    repl._meta(":methods missing_thing")
    assert "poop:" in capsys.readouterr().err


def test_meta_explain_statement_uses_validator_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    repl, _ = _repl()
    repl._meta(":explain if")
    out = capsys.readouterr().out
    assert "if_true" in out
    assert "(line" not in out


def test_meta_explain_builtin_call(capsys: pytest.CaptureFixture[str]) -> None:
    repl, _ = _repl()
    repl._meta(":explain len")
    assert "obj.len()" in capsys.readouterr().out


def test_meta_explain_fstring(capsys: pytest.CaptureFixture[str]) -> None:
    repl, _ = _repl()
    repl._meta(":explain fstring")
    assert "forbidden" in capsys.readouterr().out


def test_meta_explain_unknown_lists_known_constructs(
    capsys: pytest.CaptureFixture[str],
) -> None:
    repl, _ = _repl()
    repl._meta(":explain banana")
    out = capsys.readouterr().out
    assert "Known constructs" in out
    assert "if" in out


def test_meta_explain_unknown_does_not_claim_the_construct_is_allowed(
    capsys: pytest.CaptureFixture[str],
) -> None:
    repl, _ = _repl()
    repl._meta(":explain banana")
    assert "may simply be allowed" not in capsys.readouterr().out


@pytest.mark.parametrize(
    ("topic", "expected"),
    [
        ("import", "not the library"),
        ("invert", "bit_invert"),
        ("unary_minus", "negated"),
        ("unary_plus", "write the value directly"),
        ("type_alias", "type aliases are forbidden"),
        ("delattr", "del_attr"),
        ("__import__", "forbidden"),
    ],
)
def test_meta_explain_covers_banned_constructs(
    topic: str, expected: str, capsys: pytest.CaptureFixture[str]
) -> None:
    repl, _ = _repl()
    repl._meta(f":explain {topic}")
    assert expected in capsys.readouterr().out


# These three answer name *choices* rather than constructs — there is no word a
# learner could type at `:explain` to reach them, so they are topicless by
# design.
_EXPLAIN_EXEMPT = {
    "NoBuiltinShadowValidator",
    "NoNamespaceShadowValidator",
    "NoPoopPrefixValidator",
}


def test_every_validator_is_reachable_from_explain() -> None:
    # `:explain` answers with the validator's own message, reached by running a
    # snippet through it — so a validator that no topic trips can never be
    # explained, and the fallback says nothing is known about it. The
    # call-name topics are derived and cannot drift; the syntax snippets are
    # hand-written, which is how `import`, `invert`, the unary operators and
    # `type_alias` went missing in the first place.
    names = {id(o): n for n, o in vars(validators).items() if isinstance(o, type)}
    snippets = [_explain_snippet(t) for t in _EXPLAIN_CALLS | set(_EXPLAIN_SNIPPETS)]

    def trips(validator: object, source: str | None) -> bool:
        if source is None:
            return False
        try:
            validator.validate(ast.parse(source))  # ty: ignore[unresolved-attribute]
        except ValidationError:
            return True
        return False

    unreachable = {
        names.get(id(type(v)), repr(v))
        for v in DEFAULT_VALIDATORS
        if not any(trips(v, s) for s in snippets)
    }
    assert sorted(unreachable - _EXPLAIN_EXEMPT) == []


def test_meta_explain_without_arg_shows_usage(
    capsys: pytest.CaptureFixture[str],
) -> None:
    repl, _ = _repl()
    repl._meta(":explain")
    assert "usage" in capsys.readouterr().out


def test_meta_explain_every_known_construct_produces_output(
    capsys: pytest.CaptureFixture[str],
) -> None:
    repl, _ = _repl()
    for construct in sorted(_EXPLAIN_CALLS | set(_EXPLAIN_SNIPPETS)):
        repl._meta(f":explain {construct}")
        out = capsys.readouterr().out
        # Asserting `"forbidden" in out` only proxied for "a validator spoke",
        # and held by luck of wording: no_unary_minus says "allowed only on
        # numeric literals" instead. Assert the two non-explanations directly.
        assert f"{construct} is allowed in POOP." not in out, construct
        assert "no :explain topic" not in out, construct


def test_meta_help_lists_commands(capsys: pytest.CaptureFixture[str]) -> None:
    repl, _ = _repl()
    repl._meta(":help")
    out = capsys.readouterr().out
    assert ":methods" in out
    assert ":explain" in out


def test_meta_unknown_command_suggests_help(
    capsys: pytest.CaptureFixture[str],
) -> None:
    repl, _ = _repl()
    repl._meta(":banana")
    assert ":help" in capsys.readouterr().err


def test_run_dispatches_meta_command(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repl = Repl(Interpreter())
    monkeypatch.setattr("builtins.input", _fake_input(":explain if", EOFError()))
    repl.run()
    assert "if_true" in capsys.readouterr().out


def test_run_meta_command_does_not_touch_buffer(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repl = Repl(Interpreter())
    monkeypatch.setattr(
        "builtins.input", _fake_input(":help", "x = 1 + 1", "x", EOFError())
    )
    repl.run()
    assert repl._ns.get("x") == Int(2)


# --- _is_safe_expr ---


def test_is_safe_expr_rejects_syntax_error() -> None:
    from poop.repl import _is_safe_expr

    assert _is_safe_expr("1 +") is False
    assert _is_safe_expr("x") is True


# --- readline unavailable / history fallbacks ---


def test_setup_readline_without_readline_module_is_a_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A build without readline (`import readline` raising) must degrade quietly.
    monkeypatch.setitem(sys.modules, "readline", None)
    _setup_readline({})


def test_setup_readline_missing_history_file_is_ignored(
    monkeypatch: pytest.MonkeyPatch, tmp_path: object
) -> None:
    from pathlib import Path

    import poop.repl as repl

    monkeypatch.setattr(repl, "_HISTORY_FILE", Path(str(tmp_path)) / "does_not_exist")
    _setup_readline({})


def test_save_history_swallows_write_errors(
    monkeypatch: pytest.MonkeyPatch, tmp_path: object
) -> None:
    from pathlib import Path

    import poop.repl as repl

    # A history path under a missing directory makes write_history_file raise;
    # the saver must swallow it so a crash at exit is impossible.
    monkeypatch.setattr(repl, "_HISTORY_FILE", Path(str(tmp_path)) / "nope" / "hist")
    _save_history()


def test_readline_input_without_readline_falls_back_to_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from poop.repl import _readline_input

    monkeypatch.setitem(sys.modules, "readline", None)
    monkeypatch.setattr("builtins.input", lambda prompt="": "typed")
    assert _readline_input(">>> ", "    ") == "typed"


def test_readline_input_pre_hook_inserts_indent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import readline

    from poop.repl import _readline_input

    calls: dict[str, object] = {}
    monkeypatch.setattr(
        readline, "insert_text", lambda s: calls.__setitem__("insert", s)
    )
    monkeypatch.setattr(
        readline, "redisplay", lambda: calls.__setitem__("redisplay", True)
    )
    # Fire the registered pre-input hook synchronously so its body runs.
    monkeypatch.setattr(
        readline,
        "set_pre_input_hook",
        lambda hook: hook() if hook is not None else None,
    )
    monkeypatch.setattr("builtins.input", lambda prompt="": "line")
    assert _readline_input(">>> ", "    ") == "line"
    assert calls["insert"] == "    "
    assert calls["redisplay"] is True


# --- run(): syntax error in a completed buffer ---


def test_run_syntax_error_clears_buffer_and_continues(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # A definitive syntax error (not an incomplete line) is reported and the
    # buffer reset, so the next line starts fresh rather than re-parsing junk.
    monkeypatch.setattr(
        "builtins.input", _fake_input(")", "x = 1 + 1", "x", EOFError())
    )
    repl = Repl(Interpreter())
    repl.run()
    assert "poop:" in capsys.readouterr().err
    assert repl._ns.get("x") == Int(2)


# --- :explain when the construct turns out to be allowed ---


def test_meta_explain_reports_an_allowed_construct(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # If a topic's snippet trips no validator, `:explain` says so plainly rather
    # than pretending it is forbidden.
    import poop.repl as repl

    monkeypatch.setitem(repl._EXPLAIN_SNIPPETS, "noop", "x")
    r, _ = _repl()
    r._meta(":explain noop")
    assert "noop is allowed in POOP." in capsys.readouterr().out
