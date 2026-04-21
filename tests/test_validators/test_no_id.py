import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_id import NoIdValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoIdValidator().validate(tree)


def test_id_call_raises_validation_error() -> None:
    tree = ast.parse("id(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoIdValidator().validate(tree)
    assert "id()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("id(x)")
    with pytest.raises(ValidationError, match="obj.id()"):
        NoIdValidator().validate(tree)


def test_id_carries_line_number() -> None:
    tree = ast.parse("x = 1\nid(x)")
    with pytest.raises(ValidationError) as exc_info:
        NoIdValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_id_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.id()")
    NoIdValidator().validate(tree)
