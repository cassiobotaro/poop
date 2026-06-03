import subprocess
import sys
from pathlib import Path

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


def test_cli_exits_with_error_on_invalid_code(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_text("print('x')\n", encoding="utf-8")
    result = runner.invoke(app, [str(f)])
    assert result.exit_code == 1
    assert "poop:" in result.output


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
