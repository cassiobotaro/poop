"""`@` applies an arbitrary expression, which no validator used to check.

`INFECTIONS.md` reasons about `staticmethod`, `classmethod` and `property` —
"class-definition decorators, not runtime operations on values" — and allows
them. The boundary was written down twice (there, and in `_ALLOWED_BUILTINS`)
and enforced nowhere, so a plain block silently replaced a method.
"""

import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_decorator import ALLOWED, NoDecoratorValidator


def _validate(source: str) -> None:
    NoDecoratorValidator().validate(ast.parse(source))


@pytest.mark.parametrize("name", ALLOWED)
def test_the_three_class_definition_decorators_are_allowed(name: str) -> None:
    _validate(f"class Foo:\n    @{name}\n    def bar():\n        pass")


def test_an_arbitrary_decorator_is_refused() -> None:
    with pytest.raises(ValidationError, match=r"decorator @twice is forbidden"):
        _validate("class Foo:\n    @twice\n    def bar():\n        pass")


def test_the_message_names_the_allowed_three() -> None:
    with pytest.raises(ValidationError, match="@staticmethod, @classmethod, @property"):
        _validate("class Foo:\n    @twice\n    def bar():\n        pass")


def test_a_called_decorator_is_refused_even_when_allowed_bare() -> None:
    # `@staticmethod(...)` is a runtime call, which is the distinction the
    # allowance rests on.
    with pytest.raises(ValidationError, match=r"decorator @staticmethod\(\.\.\.\)"):
        _validate("class Foo:\n    @staticmethod()\n    def bar():\n        pass")


def test_an_attribute_decorator_is_refused() -> None:
    with pytest.raises(ValidationError, match=r"decorator @a\.b is forbidden"):
        _validate("class Foo:\n    @a.b\n    def bar():\n        pass")


def test_a_decorated_class_is_refused_too() -> None:
    with pytest.raises(ValidationError, match=r"decorator @twice is forbidden"):
        _validate("@twice\nclass Foo:\n    pass")


def test_a_decorated_async_method_is_refused_on_the_way() -> None:
    # `async def` is rejected by no_async in its own right; the decorator on
    # one must not slip through while that happens.
    with pytest.raises(ValidationError, match=r"decorator @twice is forbidden"):
        _validate("class Foo:\n    @twice\n    async def bar():\n        pass")


def test_an_unusual_spelling_falls_back_to_the_source() -> None:
    with pytest.raises(ValidationError, match=r"decorator @\(a, b\) is forbidden"):
        _validate("class Foo:\n    @(a, b)\n    def bar():\n        pass")


def test_collect_reports_every_decorator() -> None:
    errors = NoDecoratorValidator().collect(
        ast.parse(
            "class Foo:\n    @one\n    @two\n    def bar():\n        pass\n"
            "class Baz:\n    @three\n    def qux():\n        pass"
        )
    )
    assert len(errors) == 3


def test_an_undecorated_program_is_accepted() -> None:
    _validate("class Foo:\n    def bar():\n        pass")
