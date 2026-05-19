import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_unary_minus import NoUnaryMinusValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoUnaryMinusValidator().validate(tree)


def test_negative_literal_is_allowed() -> None:
    tree = ast.parse("x = -1")
    NoUnaryMinusValidator().validate(tree)


def test_negative_float_literal_is_allowed() -> None:
    tree = ast.parse("x = -3.14")
    NoUnaryMinusValidator().validate(tree)


def test_unary_minus_on_variable_raises() -> None:
    tree = ast.parse("x = -y")
    with pytest.raises(ValidationError) as exc_info:
        NoUnaryMinusValidator().validate(tree)
    assert "negated()" in str(exc_info.value)


def test_unary_minus_on_call_raises() -> None:
    tree = ast.parse("x = -foo()")
    with pytest.raises(ValidationError, match=r"\.negated"):
        NoUnaryMinusValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    tree = ast.parse("a = 1\nb = -c")
    with pytest.raises(ValidationError) as exc_info:
        NoUnaryMinusValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_nested_unary_minus_inside_class_is_rejected() -> None:
    source = "class Foo:\n    def bar(self):\n        return -self.x"
    tree = ast.parse(source)
    with pytest.raises(ValidationError, match=r"\.negated"):
        NoUnaryMinusValidator().validate(tree)


def test_bitwise_invert_is_not_affected() -> None:
    tree = ast.parse("x = ~y")
    NoUnaryMinusValidator().validate(tree)


def test_negative_complex_literal_is_allowed() -> None:
    tree = ast.parse("x = -1.5j")
    NoUnaryMinusValidator().validate(tree)


def test_unary_minus_on_true_is_rejected() -> None:
    # bool subclasses int in Python, but POOP treats Boolean as its own
    # type — negating a boolean literal must fail.
    tree = ast.parse("x = -True")
    with pytest.raises(ValidationError, match=r"numeric literals"):
        NoUnaryMinusValidator().validate(tree)


def test_unary_minus_on_false_is_rejected() -> None:
    tree = ast.parse("x = -False")
    with pytest.raises(ValidationError, match=r"numeric literals"):
        NoUnaryMinusValidator().validate(tree)


def test_unary_minus_on_double_negation_is_rejected() -> None:
    # `-(-3)` parses as `UnaryOp(USub, UnaryOp(USub, Constant(3)))` — the
    # outer operand is an expression, not a literal, so it must fail.
    tree = ast.parse("x = -(-3)")
    with pytest.raises(ValidationError, match=r"numeric literals"):
        NoUnaryMinusValidator().validate(tree)


def test_unary_minus_on_parenthesised_literal_is_rejected() -> None:
    # `-(3)` collapses to the same AST as `-3`, so this still passes
    # — included for documentation, not a behavioural assertion.
    tree = ast.parse("x = -(3)")
    NoUnaryMinusValidator().validate(tree)


def test_unary_minus_on_string_constant_is_rejected() -> None:
    # `Constant` covers more than numbers; only numeric literals get
    # the `-` privilege.
    tree = ast.parse('x = -"foo"')
    with pytest.raises(ValidationError, match=r"numeric literals"):
        NoUnaryMinusValidator().validate(tree)


def test_unary_minus_on_none_constant_is_rejected() -> None:
    tree = ast.parse("x = -None")
    with pytest.raises(ValidationError, match=r"numeric literals"):
        NoUnaryMinusValidator().validate(tree)
