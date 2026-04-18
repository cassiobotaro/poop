from pathlib import Path

import pytest

from poop import Interpreter
from poop.errors import ExecutionError, ParseError, ValidationError


def test_valid_code_runs_successfully() -> None:
    Interpreter().run_source("x = 1 + 2")


def test_syntax_error_raises_parse_error() -> None:
    with pytest.raises(ParseError):
        Interpreter().run_source("def :")


def test_if_statement_raises_validation_error() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Interpreter().run_source("if True:\n    pass")
    assert "if statements" in str(exc_info.value)


def test_if_expression_raises_validation_error() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Interpreter().run_source("x = 1 if True else 2")
    assert "ternary" in str(exc_info.value)


def test_error_message_includes_line_number() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Interpreter().run_source("x = 1\nif True:\n    pass")
    assert "line 2" in str(exc_info.value)


def test_runtime_error_raises_execution_error() -> None:
    with pytest.raises(ExecutionError):
        Interpreter().run_source("raise ValueError('runtime failure')")


def test_custom_validators_replace_defaults() -> None:
    Interpreter(validators=[]).run_source("if True:\n    pass")


def test_run_file_reads_and_executes(tmp_path: Path) -> None:
    f = tmp_path / "hello.py"
    f.write_text("x = 42\n", encoding="utf-8")
    Interpreter().run_file(f)
