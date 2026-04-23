import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_try import NoTryValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoTryValidator().validate(tree)


def test_try_except_raises_validation_error() -> None:
    source = "try:\n    pass\nexcept Exception:\n    pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError) as exc_info:
        NoTryValidator().validate(tree)
    assert "try/except" in str(exc_info.value)


def test_try_finally_raises_validation_error() -> None:
    source = "try:\n    pass\nfinally:\n    pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoTryValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    source = "x = 1\ntry:\n    pass\nexcept Exception:\n    pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError) as exc_info:
        NoTryValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_nested_try_inside_class_is_rejected() -> None:
    source = "class Foo:\n    def bar(self):\n        try:\n            pass\n        except Exception:\n            pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoTryValidator().validate(tree)


def test_try_except_star_raises_validation_error() -> None:
    source = "try:\n    pass\nexcept* Exception:\n    pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError, match="on_error"):
        NoTryValidator().validate(tree)


def test_error_message_mentions_on_error() -> None:
    source = "try:\n    pass\nexcept Exception:\n    pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError, match="on_error"):
        NoTryValidator().validate(tree)
