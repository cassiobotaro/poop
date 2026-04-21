import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_del import NoDelValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoDelValidator().validate(tree)


def test_del_raises_validation_error() -> None:
    tree = ast.parse("del x")
    with pytest.raises(ValidationError, match="del"):
        NoDelValidator().validate(tree)


def test_error_message_mentions_destruction() -> None:
    tree = ast.parse("del x")
    with pytest.raises(ValidationError, match="destruction"):
        NoDelValidator().validate(tree)


def test_del_carries_line_number() -> None:
    tree = ast.parse("x = 1\ndel x")
    with pytest.raises(ValidationError) as exc_info:
        NoDelValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_del_multiple_targets_raises() -> None:
    tree = ast.parse("del x, y")
    with pytest.raises(ValidationError):
        NoDelValidator().validate(tree)
