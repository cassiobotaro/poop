import ast

import pytest

from poop.errors import ValidationError
from poop.interpreter import Interpreter
from poop.validators.no_class_machinery import NoClassMachineryValidator


def _validate(source: str) -> None:
    NoClassMachineryValidator().validate(ast.parse(source))


@pytest.mark.parametrize(
    "source",
    [
        "property.print()",
        "p = property",
        "p = property(lambda s: 1)",
        "classmethod(f)",
        "staticmethod(f)",
        "f(staticmethod)",
        "class C:\n    x = property",
    ],
)
def test_the_three_decorators_are_refused_outside_a_decorator(source: str) -> None:
    # `_ALLOWED_BUILTINS` admits them as class-definition machinery, and
    # INFECTIONS.md scopes that to `@`: "a called decorator is a runtime
    # operation, which is the distinction the allowance rests on". Reachable
    # as plain names they answered Python — `type object 'property' has no
    # attribute 'print'` — the naked-native symptom the allow-list ended.
    with pytest.raises(ValidationError, match="only as a decorator"):
        _validate(source)


@pytest.mark.parametrize("name", ["staticmethod", "classmethod", "property"])
def test_the_three_decorators_stay_legal_on_an_at(name: str) -> None:
    _validate(f"class C:\n    @{name}\n    def m():\n        pass")


def test_super_is_refused_uncalled() -> None:
    with pytest.raises(ValidationError, match="call it"):
        _validate("s = super")


def test_super_stays_legal_called() -> None:
    _validate("class C:\n    def m(self):\n        super().m()")


def test_a_dunder_machinery_name_is_left_to_no_dunder_name() -> None:
    # `__build_class__` and `__name__` are the other two `_ALLOWED_BUILTINS`
    # entries; both are dunders, and `no_dunder_name` owns that half.
    _validate("__build_class__")


def test_ordinary_names_are_untouched() -> None:
    _validate("x = 1\ny = x.upper()")


def test_the_leak_is_closed_end_to_end() -> None:
    with pytest.raises(ValidationError, match="only as a decorator"):
        Interpreter().run_source("property.print()")
