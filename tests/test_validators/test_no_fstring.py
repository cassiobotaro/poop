import ast

import pytest

from poop.errors import ValidationError
from poop.interpreter import Interpreter
from poop.validators.no_fstring import NoFstringValidator


def test_plain_string_passes() -> None:
    tree = ast.parse('x = "hello"')
    NoFstringValidator().validate(tree)


def test_concatenation_passes() -> None:
    tree = ast.parse('x = "Hello, " + name + "!"')
    NoFstringValidator().validate(tree)


def test_interpolated_fstring_raises() -> None:
    tree = ast.parse('x = f"hi {n}"')
    with pytest.raises(ValidationError) as exc_info:
        NoFstringValidator().validate(tree)
    assert "f-string" in str(exc_info.value)


def test_constant_fstring_also_raises() -> None:
    # f"hello" (no interpolation) still parses to a JoinedStr, so it is
    # forbidden too — the user should drop the f prefix.
    tree = ast.parse('x = f"hello"')
    with pytest.raises(ValidationError):
        NoFstringValidator().validate(tree)


def test_error_suggests_concatenation() -> None:
    tree = ast.parse('x = f"hi {n}"')
    with pytest.raises(ValidationError, match="concatenation"):
        NoFstringValidator().validate(tree)


def test_fstring_carries_line_number() -> None:
    tree = ast.parse('x = 1\ny = f"hi {n}"')
    with pytest.raises(ValidationError) as exc_info:
        NoFstringValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_fstring_rejected_by_default_pipeline() -> None:
    # Regression: an interpolated f-string used to pass validation and then
    # silently corrupt at runtime (literal segments wrapped in _poop_str
    # Calls inside the JoinedStr). It must now be rejected up front.
    with pytest.raises(ValidationError):
        Interpreter().run_source('n = 5\nf"hi {n}".print()')
