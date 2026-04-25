import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_type_alias import NoTypeAliasValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoTypeAliasValidator().validate(tree)


def test_type_alias_raises_validation_error() -> None:
    tree = ast.parse("type X = int")
    with pytest.raises(ValidationError):
        NoTypeAliasValidator().validate(tree)


def test_error_message_mentions_type_aliases() -> None:
    tree = ast.parse("type X = int")
    with pytest.raises(ValidationError, match="type aliases"):
        NoTypeAliasValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    tree = ast.parse("x = 1\ntype X = int")
    with pytest.raises(ValidationError) as exc_info:
        NoTypeAliasValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_type_alias_inside_class_is_rejected() -> None:
    source = "class Foo:\n    type X = int"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoTypeAliasValidator().validate(tree)
