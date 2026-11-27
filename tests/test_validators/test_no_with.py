import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_with import NoWithValidator


def test_with_statement_raises_validation_error() -> None:
    source = "with open('f') as f:\n    pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError) as exc_info:
        NoWithValidator().validate(tree)
    assert "with" in str(exc_info.value).lower()


def test_error_message_mentions_with_builder() -> None:
    source = "with open('f') as f:\n    pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError, match="With"):
        NoWithValidator().validate(tree)


def test_validation_error_carries_line_number() -> None:
    source = "x = 1\nwith open('f') as f:\n    pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError) as exc_info:
        NoWithValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_nested_with_inside_class_is_rejected() -> None:
    source = (
        "class Foo:\n    def bar(self):\n        with open('f') as f:\n            pass"
    )
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoWithValidator().validate(tree)


def test_with_without_as_raises_validation_error() -> None:
    source = "with lock:\n    pass"
    tree = ast.parse(source)
    with pytest.raises(ValidationError):
        NoWithValidator().validate(tree)


def test_async_with_raises_validation_error() -> None:
    source = (
        "class P:\n    async def m(self):\n        async with cm:\n            pass"
    )
    with pytest.raises(ValidationError) as exc_info:
        NoWithValidator().validate(ast.parse(source))
    assert exc_info.value.message == (
        "async with is forbidden — use "
        "AsyncWith(lambda: cm).do(lambda resource: …).await_() instead"
    )
