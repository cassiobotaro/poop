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


def _errors(source: str) -> list[ValidationError]:
    return NoClassMachineryValidator().collect(ast.parse(source))


_IN_METHOD = "class C(P):\n    def m(self):\n        return {expr}"


def test_super_inside_a_lambda_is_refused() -> None:
    # A lambda owns no class cell, so CPython answered `RuntimeError: super():
    # no arguments` at run time — about a cell the block cannot be given.
    (error,) = _errors(_IN_METHOD.format(expr="(lambda: super().m())()"))
    assert error.message == (
        "super() inside a lambda is forbidden — send it from the method and "
        "hand the block its answer"
    )
    assert error.lineno == 3


def test_super_directly_in_a_method_passes() -> None:
    assert _errors(_IN_METHOD.format(expr="super().m()")) == []


def test_super_in_a_method_called_from_a_lambda_passes() -> None:
    # The block receives the method's answer; `super()` itself sits in a def.
    assert _errors(_IN_METHOD.format(expr="(lambda x: x)(super().m())")) == []


def test_a_value_returned_from_init_is_refused() -> None:
    (error,) = _errors("class C:\n    def __init__(self):\n        return 5")
    assert error.message == (
        "return with a value in __init__ is forbidden — __init__ builds the "
        "receiver and answers nothing"
    )
    assert error.lineno == 3


def test_a_bare_return_in_init_passes() -> None:
    assert _errors("class C:\n    def __init__(self):\n        return") == []


def test_a_return_in_a_def_nested_in_init_passes() -> None:
    source = (
        "class C:\n    def __init__(self):\n        def inner():\n"
        "            return 5\n        self.f = inner"
    )
    assert _errors(source) == []
