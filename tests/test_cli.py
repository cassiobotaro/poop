import io
import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from poop import cli
from poop.cli import app
from tests._support import REPO_ROOT, FeedInput, SourceFile, console

runner = CliRunner()


def test_cli_runs_valid_file(source_file: SourceFile) -> None:
    f = source_file('"hi".print()\n', "ok.py")
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


def test_cli_exits_with_error_on_invalid_code(source_file: SourceFile) -> None:
    f = source_file("print('x')\n", "bad.py")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 1
    assert "poop:" in result.output


def test_cli_missing_file_shows_clean_diagnostic(tmp_path: Path) -> None:
    # An unreadable path is a user mistake, not a traceback.
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


def test_cli_error_shows_source_line_with_caret(source_file: SourceFile) -> None:
    f = source_file("x = 1\ny = len(x)\n", "bad.py")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 1
    assert "  2 | y = len(x)" in result.output
    assert "    |     ^" in result.output


def test_cli_caret_column_matches_offset(source_file: SourceFile) -> None:
    f = source_file("if x:\n    pass\n", "bad.py")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 1
    assert "  1 | if x:" in result.output
    assert "    | ^" in result.output


def test_cli_runtime_error_shows_line_without_caret(source_file: SourceFile) -> None:
    f = source_file("x = 1\ny = x / 0\n", "boom.py")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 1
    assert "  2 | y = x / 0" in result.output
    assert "^" not in result.output


def test_cli_validators_only_no_errors(source_file: SourceFile) -> None:
    f = source_file('"hi".print()\n', "ok.py")
    result = runner.invoke(app, [str(f), "--validators-only"])
    assert result.exit_code == 0
    assert "No validation errors." in result.output


def test_cli_validators_only_reports_all_errors(source_file: SourceFile) -> None:
    f = source_file("if x:\n    print(x)\n", "bad.py")
    result = runner.invoke(app, [str(f), "--validators-only"])
    assert result.exit_code == 1
    # Both if and print should be reported
    assert "if" in result.output
    assert "print" in result.output


def test_cli_validators_only_shows_snippet_per_error(source_file: SourceFile) -> None:
    f = source_file("if x:\n    print(x)\n", "bad.py")
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


def test_cli_transformers_only_dumps_ast(source_file: SourceFile) -> None:
    f = source_file('"hi".print()\n', "ok.py")
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


def test_main_module_runs_file_via_argv(source_file: SourceFile) -> None:
    # Regression: `python main.py <file>` used to call the command function
    # directly (file=None default), ignoring argv and dropping into the REPL.
    # Run it as a subprocess so the wiring in main.py is exercised end to end.
    f = source_file('"hi".print()\n', "ok.py")
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


def test_an_error_is_syntax_highlighted_on_a_terminal(
    monkeypatch: pytest.MonkeyPatch, source_file: SourceFile
) -> None:
    # On a colour stderr, a PoopError is rendered via render_error (coloured,
    # highlighted) rather than the plain format_error string.
    buf = io.StringIO()
    monkeypatch.setattr(cli, "ERR", console(buf))
    f = source_file("if x:\n    pass\n", "bad.py")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 1
    out = buf.getvalue()
    assert "\x1b[" in out
    assert "poop: if statements are forbidden" in out


def test_cli_no_file_starts_the_repl(feed_input: FeedInput) -> None:
    # `poop` with no argument drops into the REPL; an immediate EOF exits it 0.
    feed_input(EOFError())
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "POOP" in result.output


def test_cli_transformers_only_colorizes_on_a_terminal(
    monkeypatch: pytest.MonkeyPatch, source_file: SourceFile
) -> None:
    buf = io.StringIO()
    monkeypatch.setattr(cli, "OUT", console(buf))
    f = source_file('"hi".print()\n', "ok.py")
    result = runner.invoke(app, [str(f), "--transformers-only"])
    assert result.exit_code == 0
    out = buf.getvalue()
    assert "\x1b[" in out  # syntax-highlighted AST dump
    assert "_poop_str" in out


def test_entry_point_invokes_the_typer_app(monkeypatch: pytest.MonkeyPatch) -> None:
    called: list[bool] = []
    monkeypatch.setattr(cli, "app", lambda: called.append(True))
    cli.entry_point()
    assert called == [True]
