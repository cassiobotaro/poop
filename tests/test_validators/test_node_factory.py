import ast

import pytest

from poop.errors import ValidationError
from poop.validators._node import make_node_validator


def test_single_node_validator_rejects_target() -> None:
    Validator = make_node_validator({ast.Assert: "no asserts"})

    with pytest.raises(ValidationError, match="no asserts"):
        Validator().validate(ast.parse("assert True"))


def test_single_node_validator_accepts_other_code() -> None:
    Validator = make_node_validator({ast.Assert: "no asserts"})

    Validator().validate(ast.parse("x = 1\ny = x + 2"))


def test_multi_node_validator_handles_each_type() -> None:
    Validator = make_node_validator(
        {
            ast.Global: "no global",
            ast.Nonlocal: "no nonlocal",
        }
    )

    with pytest.raises(ValidationError, match="no global"):
        Validator().validate(ast.parse("def f():\n    global x\n    x = 1"))
    with pytest.raises(ValidationError, match="no nonlocal"):
        Validator().validate(
            ast.parse("def outer():\n    def f():\n        nonlocal y")
        )


def test_validator_reports_lineno_and_col_offset() -> None:
    Validator = make_node_validator({ast.Assert: "no asserts"})

    with pytest.raises(ValidationError) as excinfo:
        Validator().validate(ast.parse("x = 1\nassert False"))
    assert excinfo.value.lineno == 2
    assert excinfo.value.col_offset == 0


def test_validator_does_not_recurse_into_banned_node() -> None:
    Validator = make_node_validator({ast.Assert: "no asserts"})

    with pytest.raises(ValidationError, match="no asserts"):
        Validator().validate(ast.parse("assert True"))


def test_factory_returns_independent_classes() -> None:
    A = make_node_validator({ast.Assert: "A"})
    B = make_node_validator({ast.Global: "B"})

    with pytest.raises(ValidationError, match="A"):
        A().validate(ast.parse("assert True"))
    B().validate(ast.parse("assert True"))
