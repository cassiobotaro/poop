import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_try import NoTryValidator


def test_try_except_raises_validation_error() -> None:
    source = "try:\n    pass\nexcept Exception:\n    pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError, match="try/except"):
        NoTryValidator().validate(tree)


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


def test_try_except_star_is_a_definitive_ban() -> None:
    source = "try:\n    pass\nexcept* ValueError:\n    pass"
    with pytest.raises(ValidationError) as exc_info:
        NoTryValidator().validate(ast.parse(source))
    assert exc_info.value.message == (
        "try/except* is forbidden — nothing in POOP raises an exception group"
    )
    assert exc_info.value.lineno == 1


def test_try_except_names_the_try_substitute() -> None:
    source = "try:\n    pass\nexcept ValueError:\n    pass"
    with pytest.raises(ValidationError) as exc_info:
        NoTryValidator().validate(ast.parse(source))
    assert exc_info.value.message == (
        "try/except is forbidden — use Try(block).except_(ExcType, handler).run() instead"
    )
    assert exc_info.value.lineno == 1


def test_try_else_names_the_try_substitute() -> None:
    source = "try:\n    pass\nexcept ValueError:\n    pass\nelse:\n    pass"
    with pytest.raises(ValidationError) as exc_info:
        NoTryValidator().validate(ast.parse(source))
    assert exc_info.value.message.startswith("try/except is forbidden — use Try(")


def test_error_message_mentions_try() -> None:
    source = "try:\n    pass\nexcept Exception:\n    pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError, match="Try"):
        NoTryValidator().validate(tree)
