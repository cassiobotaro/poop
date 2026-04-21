import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_exit import NoExitValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoExitValidator().validate(tree)


def test_exit_raises_validation_error() -> None:
    tree = ast.parse("exit()")
    with pytest.raises(ValidationError, match="exit()"):
        NoExitValidator().validate(tree)


def test_quit_raises_validation_error() -> None:
    tree = ast.parse("quit()")
    with pytest.raises(ValidationError, match="quit()"):
        NoExitValidator().validate(tree)


def test_exit_carries_line_number() -> None:
    tree = ast.parse("x = 1\nexit()")
    with pytest.raises(ValidationError) as exc_info:
        NoExitValidator().validate(tree)
    assert exc_info.value.lineno == 2
