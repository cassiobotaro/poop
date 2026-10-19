import io
import json
import re
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import pytest
from typer.testing import CliRunner

from poop import cli
from poop.cli import app
from tests._support import REPO_ROOT, FeedInput, SourceFile, console

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

runner = CliRunner()

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _plain(text: str) -> str:
    """`text` without colour codes.

    typer forces a colour terminal under `GITHUB_ACTIONS` and highlights
    `--flags` and quoted words inside its own usage errors, so a sentence
    asserted as one substring was split by escape codes on CI and nowhere
    else. POOP's own diagnostics go through its consoles, which only colour
    a real terminal, and need no stripping.
    """
    return _ANSI.sub("", text)


def _run_main(*args: str, **kwargs: Any) -> subprocess.CompletedProcess[str]:
    """`python -m poop <args>` in a subprocess, the module entry point."""
    return subprocess.run(  # noqa: S603
        [sys.executable, "-m", "poop", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=30,
        check=False,
        **kwargs,
    )


def test_cli_runs_valid_file(source_file: SourceFile) -> None:
    f = source_file('"hi".print()\n', "ok.py")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 0
    assert result.stdout == "hi\n"
    assert result.stderr == ""


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
    assert result.stdout == "hi\n"
    assert result.stderr == ""


@pytest.mark.parametrize(
    ("source", "code"),
    [
        (None, 1),
        ("x = (\n", 2),
        ("print(1)\n", 3),
        ("(1).at(0)\n", 4),
    ],
    ids=["unreadable", "parse", "validation", "execution"],
)
def test_cli_exit_codes_tell_the_failure_kinds_apart(
    source: str | None, code: int, source_file: SourceFile, tmp_path: Path
) -> None:
    # Every failure used to exit 1, so CI could not tell a refused program
    # from one that crashed. `None` is a file that was never written.
    path = tmp_path / "nope.py" if source is None else source_file(source)
    result = runner.invoke(app, [str(path)])
    assert result.exit_code == code
    assert "poop:" in result.stderr
    assert result.stdout == ""


def _missing(tmp_path: Path) -> Path:
    return tmp_path / "nope.py"


def _directory(tmp_path: Path) -> Path:
    return tmp_path


def _non_utf8(tmp_path: Path) -> Path:
    # Raises UnicodeDecodeError (a ValueError, not an OSError), which must
    # still yield a clean `poop:` diagnostic rather than leaking a traceback.
    f = tmp_path / "latin1.py"
    f.write_bytes(b'x = "caf\xe9".print()\n')
    return f


@pytest.mark.parametrize(
    ("make_path", "reason"),
    [
        (_missing, "No such file or directory"),
        (_directory, "Is a directory"),
        (_non_utf8, "invalid continuation byte"),
    ],
    ids=["missing-file", "directory", "non-utf8"],
)
def test_cli_an_unreadable_source_shows_a_clean_diagnostic(
    make_path: Callable[[Path], Path], reason: str, tmp_path: Path
) -> None:
    # An unreadable path is a user mistake, not a traceback.
    result = runner.invoke(app, [str(make_path(tmp_path))])
    assert result.exit_code == 1
    assert "poop: cannot read" in result.stderr
    assert reason in result.stderr
    assert "Traceback" not in result.stderr
    assert result.stdout == ""


def test_cli_error_shows_source_line_with_caret(source_file: SourceFile) -> None:
    f = source_file("x = 1\ny = len(x)\n", "bad.py")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 3
    assert "  2 | y = len(x)" in result.stderr
    assert "    |     ^" in result.stderr
    assert result.stdout == ""


def test_cli_caret_column_matches_offset(source_file: SourceFile) -> None:
    f = source_file("if x:\n    pass\n", "bad.py")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 3
    assert "  1 | if x:" in result.stderr
    assert "    | ^" in result.stderr
    assert result.stdout == ""


def test_cli_runtime_error_shows_line_without_caret(source_file: SourceFile) -> None:
    f = source_file("x = 1\ny = x / 0\n", "boom.py")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 4
    assert "  2 | y = x / 0" in result.stderr
    assert "^" not in result.stderr
    assert result.stdout == ""


_RAISES_IN_A_HANDLER = (
    "Try(lambda: 1 / 0).except_(ZeroDivisionError, lambda e: {}).run()\n"
)


@pytest.mark.parametrize(
    ("handler", "chain"),
    [
        (
            'KeyError.raise_("outer")',
            ["  while handling ZeroDivisionError: division by zero"],
        ),
        (
            'KeyError("outer").raise_from(e)',
            ["  caused by ZeroDivisionError: division by zero"],
        ),
        ('KeyError("outer").raise_from(None)', []),
    ],
    ids=["context", "cause", "suppressed"],
)
def test_cli_runtime_error_lists_the_chain_under_the_line(
    source_file: SourceFile, handler: str, chain: list[str]
) -> None:
    source = _RAISES_IN_A_HANDLER.format(handler)
    result = runner.invoke(app, [str(source_file(source))])
    assert result.exit_code == 4
    assert _plain(result.stderr).splitlines() == [
        "poop: KeyError: outer",
        f"  1 | {source.rstrip()}",
        *chain,
    ]


def test_cli_an_error_poop_composed_shows_no_chain(source_file: SourceFile) -> None:
    # Every POOP sentence is raised `from None` over CPython's own exception;
    # the report must not list that native as a link.
    result = runner.invoke(app, [str(source_file("[1].at(5)\n"))])
    assert result.exit_code == 4
    assert _plain(result.stderr).splitlines() == [
        "poop: IndexError: list has no element at 5 — it has 1 element",
        "  1 | [1].at(5)",
    ]


def test_cli_validators_only_no_errors(source_file: SourceFile) -> None:
    f = source_file('"hi".print()\n', "ok.py")
    result = runner.invoke(app, [str(f), "--validators-only"])
    assert result.exit_code == 0
    assert result.stdout == "No validation errors.\n"
    assert result.stderr == ""


def test_cli_validators_only_reports_all_errors(source_file: SourceFile) -> None:
    f = source_file("if x:\n    print(x)\n", "bad.py")
    result = runner.invoke(app, [str(f), "--validators-only"])
    assert result.exit_code == 3
    # Both if and print should be reported
    assert "if" in result.stderr
    assert "print" in result.stderr
    assert result.stdout == ""


def test_cli_validators_only_shows_snippet_per_error(source_file: SourceFile) -> None:
    f = source_file("if x:\n    print(x)\n", "bad.py")
    result = runner.invoke(app, [str(f), "--validators-only"])
    assert result.exit_code == 3
    assert "  1 | if x:" in result.stderr
    assert "  2 |     print(x)" in result.stderr
    assert "    |     ^" in result.stderr
    assert result.stdout == ""


def test_cli_validators_only_reports_parse_error(source_file: SourceFile) -> None:
    f = source_file("def (\n", "syntax.py")
    result = runner.invoke(app, [str(f), "--validators-only"])
    assert result.exit_code == 2
    assert "poop:" in result.stderr
    assert result.stdout == ""


def test_cli_validators_only_json_reports_errors_as_data(
    source_file: SourceFile,
) -> None:
    f = source_file("print(1)\nx = len([])\n", "bad.py")
    result = runner.invoke(app, [str(f), "--validators-only", "--format", "json"])
    assert result.exit_code == 3
    assert json.loads(result.stdout) == [
        {
            "line": 1,
            "col": 0,
            "message": "print() is forbidden — use obj.print() instead",
            "validator": "no_print",
        },
        {
            "line": 2,
            "col": 4,
            "message": "len() is forbidden — use obj.len() instead",
            "validator": "no_len",
        },
    ]
    assert result.stderr == ""


def test_cli_validators_only_json_on_a_clean_file_is_an_empty_array(
    source_file: SourceFile,
) -> None:
    f = source_file('"x".print()\n', "ok.py")
    result = runner.invoke(app, [str(f), "--validators-only", "--format", "json"])
    assert result.exit_code == 0
    assert result.stdout == "[]\n"
    assert result.stderr == ""


def test_cli_format_json_needs_validators_only(source_file: SourceFile) -> None:
    f = source_file('"x".print()\n', "ok.py")
    result = runner.invoke(app, [str(f), "--format", "json"])
    assert result.exit_code == 2
    assert "--format json needs --validators-only" in _plain(result.stderr)


def test_cli_transformers_only_dumps_ast(source_file: SourceFile) -> None:
    f = source_file('"hi".print()\n', "ok.py")
    result = runner.invoke(app, [str(f), "--transformers-only"])
    assert result.exit_code == 0
    assert "_poop_str" in result.output


def test_cli_a_pipe_runs_as_a_program() -> None:
    # `python3 < file` runs the file; `poop` used to answer a banner and a
    # prompt on stdout between the program's own lines. A subprocess, so
    # stdin really is a pipe. The source is read once: a second read of a
    # pipe yields nothing, which once ran the program as if blank.
    result = _run_main(input='"hello from pipe".print()\n')
    assert result.returncode == 0
    assert result.stdout == "hello from pipe\n"
    assert result.stderr == ""


def test_cli_a_piped_program_runs_in_process() -> None:
    # `CliRunner` hands the command a pipe, which is the non-tty case itself.
    result = runner.invoke(app, [], input='"x".print()\n')
    assert result.exit_code == 0
    assert result.stdout == "x\n"
    assert result.stderr == ""


def test_cli_a_dash_reads_standard_input_in_process() -> None:
    result = runner.invoke(app, ["-"], input='\ufeff"y".print()\n')
    assert result.exit_code == 0
    assert result.stdout == "y\n"


def test_cli_a_dash_is_standard_input() -> None:
    result = _run_main("-", input='"from dash".print()\n')
    assert result.returncode == 0
    assert result.stdout == "from dash\n"


def test_cli_a_piped_program_spends_its_byte_order_mark() -> None:
    result = _run_main(input='\ufeff"hi".print()\n')
    assert result.returncode == 0
    assert result.stdout == "hi\n"


def test_cli_inline_code_runs_as_a_program() -> None:
    result = runner.invoke(app, ["-c", '"abc".len().print()'])
    assert result.exit_code == 0
    assert result.stdout == "3\n"
    assert result.stderr == ""


def test_cli_inline_code_reports_with_a_gutter() -> None:
    # An error in `-c` code reports the same gutter a file gets.
    result = runner.invoke(app, ["-c", "print(1)"])
    assert result.exit_code == 3
    assert "  1 | print(1)" in result.stderr


def test_cli_version_prints_the_installed_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert re.fullmatch(r"poop \d+\.\d+.*\n", result.stdout)
    assert result.stderr == ""


@pytest.mark.parametrize("flag", ["--validators-only", "--transformers-only"])
def test_a_mode_flag_needs_a_source(
    flag: str, monkeypatch: pytest.MonkeyPatch, feed_input: FeedInput
) -> None:
    # On a terminal with nothing to run, the flag used to start the REPL and
    # say nothing about being ignored.
    monkeypatch.setattr(cli, "_stdin_is_a_terminal", lambda: True)
    feed_input(EOFError())
    result = runner.invoke(app, [flag])
    assert result.exit_code == 2
    assert f"{flag} needs a file or piped input" in _plain(result.stderr)
    assert "POOP" not in result.stdout


def test_main_module_runs_file_via_argv(source_file: SourceFile) -> None:
    # Regression: the root `main.py` once called the command function
    # directly (file=None default), ignoring argv and dropping into the REPL.
    # A subprocess, so `poop/__main__.py`'s wiring is exercised end to end.
    f = source_file('"hi".print()\n', "ok.py")
    result = _run_main(str(f), stdin=subprocess.DEVNULL)
    assert result.returncode == 0
    assert "hi" in result.stdout


def test_main_module_runs_an_example() -> None:
    result = _run_main("examples/basics/hello_world.py", stdin=subprocess.DEVNULL)
    assert result.returncode == 0
    assert result.stdout == "Hello, World!\n"


def test_an_error_is_syntax_highlighted_on_a_terminal(
    monkeypatch: pytest.MonkeyPatch, source_file: SourceFile
) -> None:
    # On a colour stderr, a PoopError is rendered via render_error (coloured,
    # highlighted) rather than the plain format_error string.
    buf = io.StringIO()
    monkeypatch.setattr(cli, "ERR", console(buf))
    f = source_file("if x:\n    pass\n", "bad.py")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 3
    out = buf.getvalue()
    assert "\x1b[" in out
    assert "poop: if statements are forbidden" in out


def test_cli_no_file_on_a_terminal_starts_the_repl(
    feed_input: FeedInput, monkeypatch: pytest.MonkeyPatch
) -> None:
    # `poop` with no argument and an interactive stdin drops into the REPL;
    # an immediate EOF exits it 0. `CliRunner` pipes stdin, so the terminal
    # is declared.
    monkeypatch.setattr(cli, "_stdin_is_a_terminal", lambda: True)
    feed_input(EOFError())
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "POOP" in result.stdout


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


def test_the_two_only_flags_cannot_be_combined(source_file: SourceFile) -> None:
    # Combined, the first one silently won and the second was dropped.
    f = source_file("x = 1\n")
    result = runner.invoke(app, [str(f), "--validators-only", "--transformers-only"])
    assert result.exit_code == 2
    assert "cannot be combined" in _plain(result.stderr)
    assert result.stdout == ""
