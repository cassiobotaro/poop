from pathlib import Path

from typer.testing import CliRunner

from poop.cli import app

runner = CliRunner()


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
