import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_unary_minus import NoUnaryMinusValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoUnaryMinusValidator().validate(tree)


def test_negative_literal_is_allowed() -> None:
    tree = ast.parse("x = -1")
    NoUnaryMinusValidator().validate(tree)


def test_negative_float_literal_is_allowed() -> None:
    tree = ast.parse("x = -3.14")
    NoUnaryMinusValidator().validate(tree)


def test_unary_minus_on_variable_raises() -> None:
    tree = ast.parse("x = -y")
    with pytest.raises(ValidationError) as exc_info:
        NoUnaryMinusValidator().validate(tree)
    assert "negated()" in str(exc_info.value)


def test_unary_minus_on_call_raises() -> None:
    tree = ast.parse("x = -foo()")
    with pytest.raises(ValidationError):
        NoUnaryMinusValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    tree = ast.parse("a = 1\nb = -c")
    with pytest.raises(ValidationError) as exc_info:
        NoUnaryMinusValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_nested_unary_minus_inside_class_is_rejected() -> None:
    source = "class Foo:\n    def bar(self):\n        return -self.x"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoUnaryMinusValidator().validate(tree)


def test_bitwise_invert_is_not_affected() -> None:
    tree = ast.parse("x = ~y")
    NoUnaryMinusValidator().validate(tree)
