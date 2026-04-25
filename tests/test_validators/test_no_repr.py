import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_repr import NoReprValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoReprValidator().validate(tree)


def test_repr_call_raises_validation_error() -> None:
    tree = ast.parse("repr(obj)")
    with pytest.raises(ValidationError) as exc_info:
        NoReprValidator().validate(tree)
    assert "repr()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("repr(obj)")
    with pytest.raises(ValidationError, match="obj.repr()"):
        NoReprValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    tree = ast.parse("x = 1\nrepr(obj)")
    with pytest.raises(ValidationError) as exc_info:
        NoReprValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_repr_is_not_rejected() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.repr()")
    NoReprValidator().validate(tree)


def test_nested_repr_inside_class_is_rejected() -> None:
    source = "class Foo:\n    def m(self):\n        return repr(self)"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoReprValidator().validate(tree)
