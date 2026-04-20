import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_is import NoIsValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoIsValidator().validate(tree)


def test_equality_is_allowed() -> None:
    tree = ast.parse("x = a == b")
    NoIsValidator().validate(tree)


def test_is_none_raises() -> None:
    tree = ast.parse("x = a is None")
    with pytest.raises(ValidationError) as exc_info:
        NoIsValidator().validate(tree)
    assert "is operator" in str(exc_info.value)


def test_is_not_none_raises() -> None:
    tree = ast.parse("x = a is not None")
    with pytest.raises(ValidationError) as exc_info:
        NoIsValidator().validate(tree)
    assert "is not operator" in str(exc_info.value)


def test_is_general_raises() -> None:
    tree = ast.parse("x = a is b")
    with pytest.raises(ValidationError):
        NoIsValidator().validate(tree)


def test_is_error_mentions_is_none() -> None:
    tree = ast.parse("x = a is None")
    with pytest.raises(ValidationError, match=r"is_none"):
        NoIsValidator().validate(tree)


def test_is_not_error_mentions_not_none() -> None:
    tree = ast.parse("x = a is not None")
    with pytest.raises(ValidationError, match=r"not_none"):
        NoIsValidator().validate(tree)


def test_error_carries_line_number() -> None:
    tree = ast.parse("x = 1\ny = a is None")
    with pytest.raises(ValidationError) as exc_info:
        NoIsValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_is_inside_class_is_rejected() -> None:
    source = "class Foo:\n    def bar(self):\n        return self is None"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoIsValidator().validate(tree)
