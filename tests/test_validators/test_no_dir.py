import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_dir import NoDirValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoDirValidator().validate(tree)


def test_dir_raises_validation_error() -> None:
    tree = ast.parse("dir(x)")
    with pytest.raises(ValidationError, match="dir()"):
        NoDirValidator().validate(tree)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("dir(x)")
    with pytest.raises(ValidationError, match="obj.dir()"):
        NoDirValidator().validate(tree)


def test_carries_line_number() -> None:
    tree = ast.parse("x = 1\ndir(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoDirValidator().validate(tree)
    assert exc_info.value.lineno == 2
