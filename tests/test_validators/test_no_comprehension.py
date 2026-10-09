import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_comprehension import NoComprehensionValidator


def test_list_comprehension_raises_validation_error() -> None:
    tree = ast.parse("[x for x in col]")
    with pytest.raises(ValidationError, match="list comprehension"):
        NoComprehensionValidator().validate(tree)


def test_set_comprehension_raises_validation_error() -> None:
    tree = ast.parse("{x for x in col}")
    with pytest.raises(ValidationError, match="set comprehension"):
        NoComprehensionValidator().validate(tree)


def test_dict_comprehension_raises_validation_error() -> None:
    tree = ast.parse("{k: v for k, v in items}")
    with pytest.raises(ValidationError, match="dict comprehension"):
        NoComprehensionValidator().validate(tree)


def test_generator_expression_raises_validation_error() -> None:
    tree = ast.parse("sum(x for x in col)")
    with pytest.raises(ValidationError, match="generator expression"):
        NoComprehensionValidator().validate(tree)


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


@pytest.mark.parametrize(
    ("source", "kind"),
    [
        ("[*xs for xs in cols]", "list comprehension"),
        ("{*xs for xs in cols}", "set comprehension"),
        ("{**d for d in dicts}", "dict comprehension"),
        ("f(*xs for xs in cols)", "generator expression"),
    ],
    ids=["list", "set", "dict", "generator"],
)
def test_unpacking_comprehension_is_the_same_ban(source: str, kind: str) -> None:
    # Python 3.15's unpacking (PEP 798) is a `Starred` element inside the
    # same four nodes, so the ban needs no new case — this pins that.
    tree = ast.parse(source)
    with pytest.raises(ValidationError, match=kind):
        NoComprehensionValidator().validate(tree)
