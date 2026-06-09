import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_type import NoTypeValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoTypeValidator().validate(tree)


def test_type_raises_validation_error() -> None:
    tree = ast.parse("type(x)")
    with pytest.raises(ValidationError, match="type()"):
        NoTypeValidator().validate(tree)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("type(x)")
    with pytest.raises(ValidationError, match="obj.class_name()"):
        NoTypeValidator().validate(tree)


def test_carries_line_number() -> None:
    tree = ast.parse("x = 1\ntype(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoTypeValidator().validate(tree)
    assert exc_info.value.lineno == 2
