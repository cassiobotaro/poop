import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_comprehension import NoComprehensionValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoComprehensionValidator().validate(tree)


def test_list_comprehension_raises_validation_error() -> None:
    tree = ast.parse("[x for x in col]")
    with pytest.raises(ValidationError) as exc_info:
        NoComprehensionValidator().validate(tree)
    assert "list comprehension" in str(exc_info.value)


def test_set_comprehension_raises_validation_error() -> None:
    tree = ast.parse("{x for x in col}")
    with pytest.raises(ValidationError) as exc_info:
        NoComprehensionValidator().validate(tree)
    assert "set comprehension" in str(exc_info.value)


def test_dict_comprehension_raises_validation_error() -> None:
    tree = ast.parse("{k: v for k, v in items}")
    with pytest.raises(ValidationError) as exc_info:
        NoComprehensionValidator().validate(tree)
    assert "dict comprehension" in str(exc_info.value)


def test_generator_expression_raises_validation_error() -> None:
    tree = ast.parse("sum(x for x in col)")
    with pytest.raises(ValidationError) as exc_info:
        NoComprehensionValidator().validate(tree)
    assert "generator expression" in str(exc_info.value)


def test_error_message_mentions_map() -> None:
    tree = ast.parse("[x for x in col]")
    with pytest.raises(ValidationError, match="map"):
        NoComprehensionValidator().validate(tree)


def test_list_comprehension_carries_line_number() -> None:
    tree = ast.parse("x = 1\n[x for x in col]")
    with pytest.raises(ValidationError) as exc_info:
        NoComprehensionValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_nested_comprehension_inside_function_is_rejected() -> None:
    source = "def foo():\n    return [x for x in col]"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoComprehensionValidator().validate(tree)
