import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_filter import NoFilterValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = [1, 2, 3]")
    NoFilterValidator().validate(tree)


def test_filter_call_raises_validation_error() -> None:
    tree = ast.parse("filter(None, [1, 2, 3])")
    with pytest.raises(ValidationError) as exc_info:
        NoFilterValidator().validate(tree)
    assert "filter()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("filter(None, [1, 2, 3])")
    with pytest.raises(ValidationError, match="col.filter"):
        NoFilterValidator().validate(tree)


def test_filter_carries_line_number() -> None:
    tree = ast.parse("x = 1\nfilter(None, [1, 2, 3])")
    with pytest.raises(ValidationError) as exc_info:
        NoFilterValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_filter_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.filter(lambda x: x)")
    NoFilterValidator().validate(tree)
