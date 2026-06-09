import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_help import NoHelpValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoHelpValidator().validate(tree)


def test_help_raises_validation_error() -> None:
    tree = ast.parse("help(x)")
    with pytest.raises(ValidationError, match="help()"):
        NoHelpValidator().validate(tree)


def test_help_without_args_raises_validation_error() -> None:
    tree = ast.parse("help()")
    with pytest.raises(ValidationError, match="help()"):
        NoHelpValidator().validate(tree)


def test_carries_line_number() -> None:
    tree = ast.parse("x = 1\nhelp(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoHelpValidator().validate(tree)
    assert exc_info.value.lineno == 2
