import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_map import NoMapValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = [1, 2, 3]")
    NoMapValidator().validate(tree)


def test_map_call_raises_validation_error() -> None:
    tree = ast.parse("map(str, [1, 2, 3])")
    with pytest.raises(ValidationError) as exc_info:
        NoMapValidator().validate(tree)
    assert "map()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse("map(str, [1, 2, 3])")
    with pytest.raises(ValidationError, match="col.map"):
        NoMapValidator().validate(tree)


def test_map_carries_line_number() -> None:
    tree = ast.parse("x = 1\nmap(str, [1, 2, 3])")
    with pytest.raises(ValidationError) as exc_info:
        NoMapValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_map_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.map(lambda x: x)")
    NoMapValidator().validate(tree)
