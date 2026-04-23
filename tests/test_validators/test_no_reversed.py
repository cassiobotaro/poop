import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_reversed import NoReversedValidator


def test_valid_code_passes() -> None:
    NoReversedValidator().validate(ast.parse("x = 1 + 2"))


def test_reversed_call_raises() -> None:
    with pytest.raises(ValidationError, match="reversed()"):
        NoReversedValidator().validate(ast.parse("reversed([1, 2, 3])"))


def test_error_suggests_method() -> None:
    with pytest.raises(ValidationError, match=r"col\.reversed\(\)"):
        NoReversedValidator().validate(ast.parse("reversed(lst)"))


def test_reversed_inside_method_raises() -> None:
    with pytest.raises(ValidationError):
        NoReversedValidator().validate(
            ast.parse("class Foo:\n    def m(self):\n        reversed(self._items)")
        )


def test_reversed_carries_line_number() -> None:
    with pytest.raises(ValidationError) as exc_info:
        NoReversedValidator().validate(ast.parse("x = 1\nreversed(lst)"))
    assert exc_info.value.lineno == 2


def test_method_named_reversed_is_not_blocked() -> None:
    NoReversedValidator().validate(
        ast.parse("class Foo:\n    def m(self):\n        self.reversed()")
    )
