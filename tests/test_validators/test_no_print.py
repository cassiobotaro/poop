import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_print import NoPrintValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoPrintValidator().validate(tree)


def test_print_call_raises_validation_error() -> None:
    tree = ast.parse('print("hello")')
    with pytest.raises(ValidationError) as exc_info:
        NoPrintValidator().validate(tree)
    assert "print" in str(exc_info.value)


def test_error_message_mentions_obj_print() -> None:
    tree = ast.parse('print("hello")')
    with pytest.raises(ValidationError, match="obj.print"):
        NoPrintValidator().validate(tree)


def test_print_inside_method_raises_validation_error() -> None:
    source = "class Foo:\n    def bar(self) -> None:\n        print('x')"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoPrintValidator().validate(tree)


def test_print_carries_line_number() -> None:
    tree = ast.parse("x = 1\nprint('hello')")
    with pytest.raises(ValidationError) as exc_info:
        NoPrintValidator().validate(tree)
    assert exc_info.value.lineno == 2
