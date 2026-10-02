import ast

import pytest

from poop.errors import ValidationError
from poop.validators._node import NodeValidator
from poop.validators.base import CollectingValidator


class _NoAssert(NodeValidator):
    messages = {ast.Assert: "no asserts"}


class _NoScopeStatements(NodeValidator):
    messages = {ast.Global: "no global", ast.Nonlocal: "no nonlocal"}


def test_single_node_validator_rejects_target() -> None:
    with pytest.raises(ValidationError, match="no asserts"):
        _NoAssert().validate(ast.parse("assert True"))


def test_single_node_validator_accepts_other_code() -> None:
    _NoAssert().validate(ast.parse("x = 1\ny = x + 2"))


def test_multi_node_validator_handles_each_type() -> None:
    with pytest.raises(ValidationError, match="no global"):
        _NoScopeStatements().validate(ast.parse("def f():\n    global x\n    x = 1"))
    with pytest.raises(ValidationError, match="no nonlocal"):
        _NoScopeStatements().validate(
            ast.parse("def outer():\n    def f():\n        nonlocal y")
        )


def test_validator_reports_lineno_and_col_offset() -> None:
    with pytest.raises(ValidationError) as excinfo:
        _NoAssert().validate(ast.parse("x = 1\nassert False"))
    assert excinfo.value.lineno == 2
    assert excinfo.value.col_offset == 0


def test_nested_banned_nodes_are_each_reported() -> None:
    # The walk descends into a rejected node: an `if` inside an `if` is two
    # rewrites, and reporting one would restore the fix-one/rerun loop.
    class _NoIf(NodeValidator):
        messages = {ast.If: "no if"}

    errors = _NoIf().collect(ast.parse("if a:\n    if b:\n        pass"))
    assert [e.lineno for e in errors] == [1, 2]


def test_subclasses_are_independent() -> None:
    with pytest.raises(ValidationError, match="no asserts"):
        _NoAssert().validate(ast.parse("assert True"))
    _NoScopeStatements().validate(ast.parse("assert True"))


def test_a_validator_with_neither_visitor_nor_collect_fails_at_definition() -> None:
    with pytest.raises(TypeError, match="sets no `visitor`"):

        class _Incomplete(CollectingValidator):
            pass
