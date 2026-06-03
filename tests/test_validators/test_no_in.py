import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_in import NoInValidator


def _validate(src: str) -> None:
    NoInValidator().validate(ast.parse(src))


def test_in_operator_raises() -> None:
    with pytest.raises(ValidationError, match=r"col\.includes\(x\)"):
        _validate("x in col")


def test_not_in_operator_raises() -> None:
    with pytest.raises(ValidationError, match=r"col\.includes\(x\)\.not_\(\)"):
        _validate("x not in col")


def test_in_inside_expression_raises() -> None:
    with pytest.raises(ValidationError):
        _validate("result = x in [1, 2, 3]")


def test_in_inside_method_raises() -> None:
    with pytest.raises(ValidationError):
        _validate(
            """
class Foo:
    def bar(self):
        return x in self._items
"""
        )


def test_in_in_chained_comparison_raises() -> None:
    # The banned `in` is the second op of a chained comparison, so the
    # validator must scan every op in node.ops, not just the first.
    with pytest.raises(ValidationError, match=r"col\.includes"):
        _validate("a < b in c")


def test_equality_allowed() -> None:
    _validate("x == y")


def test_comparison_allowed() -> None:
    _validate("x < y")


def test_is_allowed() -> None:
    _validate("x is None")
