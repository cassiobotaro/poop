import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_type_alias import NoTypeAliasValidator


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


def _errors(source: str) -> list[ValidationError]:
    return NoTypeAliasValidator().collect(ast.parse(source))


@pytest.mark.parametrize(
    ("source", "spelled"),
    [
        ("class X[T]:\n    pass", "[T]"),
        ("class X[*Ts]:\n    pass", "[*Ts]"),
        ("class X[**P]:\n    pass", "[**P]"),
        ("class C:\n    def m[T](self):\n        return T", "[T]"),
    ],
    ids=["class", "typevartuple", "paramspec", "method"],
)
def test_a_type_parameter_is_refused_as_written(source: str, spelled: str) -> None:
    (error,) = _errors(source)
    assert error.message == (
        f"type parameters are forbidden — POOP has no static types; drop the {spelled}"
    )


def test_a_generic_type_statement_reports_both() -> None:
    # The alias row and the parameter row: two rewrites, two reports.
    messages = [error.message for error in _errors("type X[T] = int")]
    assert messages[0].startswith("type aliases are forbidden")
    assert messages[1].endswith("drop the [T]")


def test_every_occurrence_is_listed_in_source_order() -> None:
    source = "class X[T]:\n    pass\n\nclass C:\n    def m[U](self):\n        pass"
    assert [error.lineno for error in _errors(source)] == [1, 5]


def test_a_plain_class_and_method_pass() -> None:
    assert _errors("class C:\n    def m(self):\n        return self") == []
