import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_getattr import NoGetattrValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoGetattrValidator().validate(tree)


def test_getattr_call_raises_validation_error() -> None:
    tree = ast.parse("getattr(obj, 'name')")
    with pytest.raises(ValidationError) as exc_info:
        NoGetattrValidator().validate(tree)
    assert "getattr()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("getattr(obj, 'name')")
    with pytest.raises(ValidationError, match="get_attr"):
        NoGetattrValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    tree = ast.parse("x = 1\ngetattr(obj, 'name')")
    with pytest.raises(ValidationError) as exc_info:
        NoGetattrValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_getattr_is_not_rejected() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.get_attr('x')")
    NoGetattrValidator().validate(tree)


def test_nested_getattr_inside_class_is_rejected() -> None:
    source = "class Foo:\n    def m(self):\n        return getattr(self, 'x')"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoGetattrValidator().validate(tree)
