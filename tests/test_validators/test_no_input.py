import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_input import NoInputValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoInputValidator().validate(tree)


def test_input_raises_validation_error() -> None:
    tree = ast.parse("input('prompt: ')")
    with pytest.raises(ValidationError, match="input()"):
        NoInputValidator().validate(tree)


def test_input_carries_line_number() -> None:
    tree = ast.parse("x = 1\ninput('prompt: ')")
    with pytest.raises(ValidationError) as exc_info:
        NoInputValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_error_suggests_str_input_method() -> None:
    tree = ast.parse("input('prompt: ')")
    with pytest.raises(ValidationError, match=r"prompt\.input\(\)"):
        NoInputValidator().validate(tree)
