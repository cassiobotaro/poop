import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_sorted import NoSortedValidator


def test_valid_code_passes() -> None:
    NoSortedValidator().validate(ast.parse("x = 1 + 2"))


def test_sorted_call_raises() -> None:
    with pytest.raises(ValidationError, match="sorted()"):
        NoSortedValidator().validate(ast.parse("sorted([3, 1, 2])"))


def test_error_suggests_method() -> None:
    with pytest.raises(ValidationError, match=r"col\.sorted\(\)"):
        NoSortedValidator().validate(ast.parse("sorted(lst)"))


def test_sorted_inside_method_raises() -> None:
    with pytest.raises(ValidationError):
        NoSortedValidator().validate(
            ast.parse("class Foo:\n    def m(self):\n        sorted(self._items)")
        )


def test_sorted_carries_line_number() -> None:
    with pytest.raises(ValidationError) as exc_info:
        NoSortedValidator().validate(ast.parse("x = 1\nsorted(lst)"))
    assert exc_info.value.lineno == 2


def test_method_named_sorted_is_not_blocked() -> None:
    NoSortedValidator().validate(
        ast.parse("class Foo:\n    def m(self):\n        self.sorted()")
    )
