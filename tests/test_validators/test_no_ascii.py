import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_ascii import NoAsciiValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoAsciiValidator().validate(tree)


def test_ascii_call_raises_validation_error() -> None:
    tree = ast.parse("ascii(obj)")
    with pytest.raises(ValidationError) as exc_info:
        NoAsciiValidator().validate(tree)
    assert "ascii()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("ascii(obj)")
    with pytest.raises(ValidationError, match="obj.ascii()"):
        NoAsciiValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    tree = ast.parse("x = 1\nascii(obj)")
    with pytest.raises(ValidationError) as exc_info:
        NoAsciiValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_ascii_is_not_rejected() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.ascii()")
    NoAsciiValidator().validate(tree)


def test_nested_ascii_inside_class_is_rejected() -> None:
    source = "class Foo:\n    def m(self):\n        return ascii(self)"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoAsciiValidator().validate(tree)
