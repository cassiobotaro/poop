import io
import subprocess
import sys
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

from poop.cli import app

runner = CliRunner()

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_cli_runs_valid_file(tmp_path: Path) -> None:
    f = tmp_path / "ok.py"
    f.write_text('"hi".print()\n', encoding="utf-8")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 0
    assert "hi\n" in result.output


def test_cli_runs_a_file_its_editor_gave_a_byte_order_mark(tmp_path: Path) -> None:
    # Editors on Windows write a BOM by default. Read as plain `utf-8` it
    # survives as a literal U+FEFF and the tokenizer answers `invalid
    # non-printable character U+FEFF` — about a character invisible in every
    # editor, from a file `python3` runs. Nothing else in the suite reads
    # bytes that are not plain ASCII.
    f = tmp_path / "bom.py"
    f.write_bytes(b"\xef\xbb\xbf" + b'"hi".print()\n')
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 0
    assert "hi\n" in result.output


def test_cli_exits_with_error_on_invalid_code(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_text("print('x')\n", encoding="utf-8")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 1
    assert "poop:" in result.output


def test_cli_missing_file_shows_clean_diagnostic(tmp_path: Path) -> None:
    # proposal 137: an unreadable path is a user mistake, not a traceback.
    missing = tmp_path / "nope.py"
    result = runner.invoke(app, [str(missing)])
    assert result.exit_code == 1
    assert "poop: cannot read" in result.output
    assert "Traceback" not in result.output


def test_cli_directory_argument_shows_clean_diagnostic(tmp_path: Path) -> None:
    result = runner.invoke(app, [str(tmp_path)])
    assert result.exit_code == 1
    assert "poop: cannot read" in result.output
    assert "Traceback" not in result.output


def test_cli_non_utf8_file_shows_clean_diagnostic(tmp_path: Path) -> None:
    # A non-UTF-8 source raises UnicodeDecodeError (a ValueError, not an
    # OSError), which must still yield a clean `poop:` diagnostic rather than
    # leaking a traceback.
    f = tmp_path / "latin1.py"
    f.write_bytes(b'x = "caf\xe9".print()\n')
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 1
    assert "poop: cannot read" in result.output
    assert "Traceback" not in result.output


def test_cli_error_shows_source_line_with_caret(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_text("x = 1\ny = len(x)\n", encoding="utf-8")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 1
    assert "  2 | y = len(x)" in result.output
    assert "    |     ^" in result.output


def test_cli_caret_column_matches_offset(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_text("if x:\n    pass\n", encoding="utf-8")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 1
    assert "  1 | if x:" in result.output
    assert "    | ^" in result.output


def test_cli_runtime_error_shows_line_without_caret(tmp_path: Path) -> None:
    f = tmp_path / "boom.py"
    f.write_text("x = 1\ny = x / 0\n", encoding="utf-8")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 1
    assert "  2 | y = x / 0" in result.output
    assert "^" not in result.output


def test_cli_validators_only_no_errors(tmp_path: Path) -> None:
    f = tmp_path / "ok.py"
    f.write_text('"hi".print()\n', encoding="utf-8")
    result = runner.invoke(app, [str(f), "--validators-only"])
    assert result.exit_code == 0
    assert "No validation errors." in result.output


def test_cli_validators_only_reports_all_errors(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_text("if x:\n    print(x)\n", encoding="utf-8")
    result = runner.invoke(app, [str(f), "--validators-only"])
    assert result.exit_code == 1
    # Both if and print should be reported
    assert "if" in result.output
    assert "print" in result.output


def test_cli_validators_only_shows_snippet_per_error(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_text("if x:\n    print(x)\n", encoding="utf-8")
    result = runner.invoke(app, [str(f), "--validators-only"])
    assert result.exit_code == 1
    assert "  1 | if x:" in result.output
    assert "  2 |     print(x)" in result.output
    assert "    |     ^" in result.output


def test_cli_validators_only_reports_parse_error(tmp_path: Path) -> None:
    f = tmp_path / "syntax.py"
    f.write_text("def (\n", encoding="utf-8")
    result = runner.invoke(app, [str(f), "--validators-only"])
    assert result.exit_code == 1
    assert "poop:" in result.output


def test_cli_transformers_only_dumps_ast(tmp_path: Path) -> None:
    f = tmp_path / "ok.py"
    f.write_text('"hi".print()\n', encoding="utf-8")
    result = runner.invoke(app, [str(f), "--transformers-only"])
    assert result.exit_code == 0
    assert "_poop_str" in result.output


def test_cli_runs_source_from_a_pipe_only_read_once() -> None:
    # Regression: the CLI read the file once for error formatting and then a
    # second time to execute it. A pipe yields its bytes only once, so the
    # executing read came back empty and the program ran as if blank —
    # printing nothing and exiting 0 instead of running the piped program.
    stdin_path = Path("/dev/stdin")
    if not stdin_path.exists():  # pragma: no cover - platform without /dev/stdin
        pytest.skip("no /dev/stdin on this platform")
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(REPO_ROOT / "main.py"), "/dev/stdin"],
        input='"hello from pipe".print()\n',
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0
    assert "hello from pipe" in result.stdout


def test_main_module_runs_file_via_argv(tmp_path: Path) -> None:
    # Regression: `python main.py <file>` used to call the command function
    # directly (file=None default), ignoring argv and dropping into the REPL.
    # Run it as a subprocess so the wiring in main.py is exercised end to end.
    f = tmp_path / "ok.py"
    f.write_text('"hi".print()\n', encoding="utf-8")
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(REPO_ROOT / "main.py"), str(f)],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        cwd=REPO_ROOT,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0
    assert "hi" in result.stdout


def _term_console(buf: io.StringIO) -> Console:
    return Console(
        file=buf, force_terminal=True, color_system="standard", no_color=False
    )


def test_emit_error_syntax_highlights_on_a_terminal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # On a colour stderr, a PoopError is rendered via render_error (coloured,
    # highlighted) rather than the plain format_error string.
    from poop import cli
    from poop.errors import ValidationError

    buf = io.StringIO()
    monkeypatch.setattr(cli, "_ERR", _term_console(buf))
    cli._emit_error(ValidationError("if is forbidden", 1, 0), "if x:")
    out = buf.getvalue()
    assert "\x1b[" in out
    assert "poop: if is forbidden" in out


def test_cli_no_file_starts_the_repl(monkeypatch: pytest.MonkeyPatch) -> None:
    # `poop` with no argument drops into the REPL; an immediate EOF exits it 0.
    def _eof(_prompt: str = "") -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", _eof)
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "POOP" in result.output


def test_cli_transformers_only_colorizes_on_a_terminal(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from poop import cli

    buf = io.StringIO()
    monkeypatch.setattr(cli, "_OUT", _term_console(buf))
    f = tmp_path / "ok.py"
    f.write_text('"hi".print()\n', encoding="utf-8")
    result = runner.invoke(app, [str(f), "--transformers-only"])
    assert result.exit_code == 0
    out = buf.getvalue()
    assert "\x1b[" in out  # syntax-highlighted AST dump
    assert "_poop_str" in out


def test_entry_point_invokes_the_typer_app(monkeypatch: pytest.MonkeyPatch) -> None:
    from poop import cli

    called: list[bool] = []
    monkeypatch.setattr(cli, "app", lambda: called.append(True))
    cli.entry_point()
    assert called == [True]
