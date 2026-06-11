import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_len import NoLenValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoLenValidator().validate(tree)


def test_len_call_raises_validation_error() -> None:
    tree = ast.parse('len("abc")')
    with pytest.raises(ValidationError) as exc_info:
        NoLenValidator().validate(tree)
    assert "len()" in str(exc_info.value)


def test_error_message_suggests_method() -> None:
    tree = ast.parse('len("abc")')
    with pytest.raises(ValidationError, match="obj.len()"):
        NoLenValidator().validate(tree)


def test_len_inside_method_raises() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        len(self)")
    with pytest.raises(ValidationError):
        NoLenValidator().validate(tree)


def test_len_carries_line_number() -> None:
    tree = ast.parse('x = 1\nlen("abc")')
    with pytest.raises(ValidationError) as exc_info:
        NoLenValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_method_named_len_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.len()")
    NoLenValidator().validate(tree)


def test_rebinding_len_is_blocked() -> None:
    # proposal 145: a bare reference to a forbidden builtin in any
    # position (here an assignment RHS) reopens the wrapper layer.
    tree = ast.parse("f = len")
    with pytest.raises(ValidationError, match="len"):
        NoLenValidator().validate(tree)


def test_len_as_argument_is_blocked() -> None:
    tree = ast.parse("words.map(len)")
    with pytest.raises(ValidationError, match="len"):
        NoLenValidator().validate(tree)


def test_len_as_reserved_assignment_target_is_blocked() -> None:
    tree = ast.parse("len = 5")
    with pytest.raises(ValidationError, match="len"):
        NoLenValidator().validate(tree)
