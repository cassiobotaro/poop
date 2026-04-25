import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_sum import NoSumValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoSumValidator().validate(tree)


def test_sum_call_raises_validation_error() -> None:
    tree = ast.parse("sum(items)")
    with pytest.raises(ValidationError) as exc_info:
        NoSumValidator().validate(tree)
    assert "sum()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("sum(items)")
    with pytest.raises(ValidationError, match="col.sum()"):
        NoSumValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    tree = ast.parse("x = 1\nsum(items)")
    with pytest.raises(ValidationError) as exc_info:
        NoSumValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_sum_is_not_rejected() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.sum()")
    NoSumValidator().validate(tree)


def test_nested_sum_inside_class_is_rejected() -> None:
    source = "class Foo:\n    def m(self):\n        return sum(self)"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoSumValidator().validate(tree)
