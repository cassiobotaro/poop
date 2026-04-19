import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_not import NoNotValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoNotValidator().validate(tree)


def test_unary_minus_is_allowed() -> None:
    tree = ast.parse("x = -1")
    NoNotValidator().validate(tree)


def test_bitwise_invert_is_allowed() -> None:
    tree = ast.parse("x = ~1")
    NoNotValidator().validate(tree)


def test_not_raises_validation_error() -> None:
    tree = ast.parse("x = not True")
    with pytest.raises(ValidationError) as exc_info:
        NoNotValidator().validate(tree)
    assert "not operator" in str(exc_info.value)


def test_error_message_mentions_not_method() -> None:
    tree = ast.parse("x = not True")
    with pytest.raises(ValidationError, match=r"\.not_\(\)"):
        NoNotValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    tree = ast.parse("x = 1\ny = not True")
    with pytest.raises(ValidationError) as exc_info:
        NoNotValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_nested_not_inside_class_is_rejected() -> None:
    source = "class Foo:\n    def bar(self):\n        return not True"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoNotValidator().validate(tree)
