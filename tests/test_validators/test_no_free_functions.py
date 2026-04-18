import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_free_functions import NoFreeFunctionsValidator


def test_valid_code_without_functions_passes() -> None:
    tree = ast.parse("x = 1 + 2")
    NoFreeFunctionsValidator().validate(tree)


def test_method_inside_class_passes() -> None:
    source = "class Foo:\n    def bar(self) -> None:\n        pass"
    tree = ast.parse(source)
    NoFreeFunctionsValidator().validate(tree)


def test_free_function_raises_validation_error() -> None:
    tree = ast.parse("def foo() -> None:\n    pass")
    with pytest.raises(ValidationError) as exc_info:
        NoFreeFunctionsValidator().validate(tree)
    assert "free functions" in str(exc_info.value)


def test_free_async_function_raises_validation_error() -> None:
    tree = ast.parse("async def foo() -> None:\n    pass")
    with pytest.raises(ValidationError) as exc_info:
        NoFreeFunctionsValidator().validate(tree)
    assert "free async functions" in str(exc_info.value)


def test_free_function_carries_line_number() -> None:
    tree = ast.parse("x = 1\ndef foo() -> None:\n    pass")
    with pytest.raises(ValidationError) as exc_info:
        NoFreeFunctionsValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_error_message_mentions_class() -> None:
    tree = ast.parse("def foo() -> None:\n    pass")
    with pytest.raises(ValidationError, match="class"):
        NoFreeFunctionsValidator().validate(tree)


def test_nested_method_inside_nested_class_passes() -> None:
    source = "class Outer:\n    class Inner:\n        def method(self) -> None:\n            pass"
    tree = ast.parse(source)
    NoFreeFunctionsValidator().validate(tree)


def test_async_method_inside_class_passes() -> None:
    source = "class Foo:\n    async def bar(self) -> None:\n        pass"
    tree = ast.parse(source)
    NoFreeFunctionsValidator().validate(tree)


def test_nested_function_inside_method_passes() -> None:
    source = "class Foo:\n    def bar(self) -> None:\n        def helper() -> None:\n            pass"
    tree = ast.parse(source)
    NoFreeFunctionsValidator().validate(tree)
