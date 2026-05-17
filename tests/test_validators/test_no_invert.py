import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_invert import NoInvertValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoInvertValidator().validate(tree)


def test_invert_on_variable_raises() -> None:
    tree = ast.parse("x = ~y")
    with pytest.raises(ValidationError) as exc_info:
        NoInvertValidator().validate(tree)
    assert "bit_invert()" in str(exc_info.value)


def test_invert_on_literal_raises() -> None:
    tree = ast.parse("x = ~1")
    with pytest.raises(ValidationError, match=r"\.bit_invert"):
        NoInvertValidator().validate(tree)


def test_invert_on_call_raises() -> None:
    tree = ast.parse("x = ~foo()")
    with pytest.raises(ValidationError, match=r"\.bit_invert"):
        NoInvertValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    tree = ast.parse("a = 1\nb = ~c")
    with pytest.raises(ValidationError) as exc_info:
        NoInvertValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_nested_invert_inside_class_is_rejected() -> None:
    source = "class Foo:\n    def bar(self):\n        return ~self.x"
    tree = ast.parse(source)
    with pytest.raises(ValidationError, match=r"\.bit_invert"):
        NoInvertValidator().validate(tree)


def test_unary_minus_on_literal_is_not_affected() -> None:
    tree = ast.parse("x = -1")
    NoInvertValidator().validate(tree)
