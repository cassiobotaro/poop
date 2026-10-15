import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_class_keyword import NoClassKeywordValidator


def _errors(source: str) -> list[ValidationError]:
    return NoClassKeywordValidator().collect(ast.parse(source))


@pytest.mark.parametrize(
    ("source", "spelled"),
    [
        ("class X(foo=1):\n    pass", "foo"),
        ("class X(Object, metaclass=Object):\n    pass", "metaclass"),
        ("class X(**opts):\n    pass", "**opts"),
    ],
    ids=["arbitrary", "metaclass", "splat"],
)
def test_a_class_keyword_is_refused_by_name(source: str, spelled: str) -> None:
    (error,) = _errors(source)
    assert error.message == (
        f"class keyword '{spelled}' is forbidden — a class is built from its bases alone"
    )


def test_the_error_points_at_the_keyword() -> None:
    (error,) = _errors("class X(Object, foo=1):\n    pass")
    assert (error.lineno, error.col_offset) == (1, 16)


def test_every_keyword_is_reported() -> None:
    assert len(_errors("class X(a=1, b=2):\n    pass")) == 2


def test_bases_alone_pass() -> None:
    assert _errors("class X(Object):\n    pass\n\nclass Y(X, list):\n    pass") == []


def test_a_call_keyword_is_not_a_class_keyword() -> None:
    assert _errors("x.print(end='')") == []


def test_validate_raises_the_first() -> None:
    with pytest.raises(ValidationError, match="class keyword 'foo'"):
        NoClassKeywordValidator().validate(ast.parse("class X(foo=1):\n    pass"))
