import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_issubclass import NoIssubclassValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoIssubclassValidator().validate(tree)


def test_issubclass_call_raises_validation_error() -> None:
    tree = ast.parse("issubclass(Dog, Animal)")
    with pytest.raises(ValidationError) as exc_info:
        NoIssubclassValidator().validate(tree)
    assert "issubclass()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("issubclass(Dog, Animal)")
    with pytest.raises(ValidationError, match="is_subclass"):
        NoIssubclassValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    tree = ast.parse("x = 1\nissubclass(Dog, Animal)")
    with pytest.raises(ValidationError) as exc_info:
        NoIssubclassValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_issubclass_is_not_rejected() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.is_subclass(Other)")
    NoIssubclassValidator().validate(tree)


def test_nested_issubclass_inside_class_is_rejected() -> None:
    source = "class Foo:\n    def m(self):\n        return issubclass(Dog, Animal)"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoIssubclassValidator().validate(tree)
