import ast
import re

import pytest

from poop.errors import ValidationError
from poop.interpreter import Interpreter
from poop.validators.no_dunder_name import NoDunderNameValidator


def _validate(source: str) -> None:
    NoDunderNameValidator().validate(ast.parse(source))


@pytest.mark.parametrize(
    "name",
    ["__builtins__", "__loader__", "__spec__", "__package__", "__debug__"],
)
def test_dunder_globals_are_rejected(name: str) -> None:
    # Every one of these is a naked Python native `exec` hands the namespace.
    with pytest.raises(ValidationError, match="dunder globals are Python's"):
        _validate(f"{name}.print()")


def test_a_dunder_with_a_substitute_names_it() -> None:
    # Shared with the attribute half, so both say one thing.
    with pytest.raises(ValidationError, match=re.escape("Klass.name()")):
        _validate("__name__.print()")


def test_the_message_is_not_dotted() -> None:
    # `.__builtins__` would name an attribute the program never wrote.
    with pytest.raises(ValidationError, match=r"^__builtins__ is forbidden"):
        _validate("__builtins__.print()")


def test_a_store_is_rejected_too() -> None:
    with pytest.raises(ValidationError, match="forbidden"):
        _validate("__name__ = 1")


def test_a_bare_init_is_rejected() -> None:
    # The `__init__` carve-out exists for `super().__init__(...)`, an
    # attribute; a bare Name has no such use.
    with pytest.raises(ValidationError, match="forbidden"):
        _validate("__init__ = 1")


def test_super_init_is_untouched() -> None:
    _validate("class C:\n    def __init__(self):\n        super().__init__()\n")


def test_ordinary_names_are_untouched() -> None:
    _validate("x.len()")
    _validate("_private = 1")
    _validate("__mangled = 1")


def test_every_occurrence_is_reported() -> None:
    errors = NoDunderNameValidator().collect(
        ast.parse("__builtins__.print()\n__loader__.print()\n")
    )
    assert len(errors) == 2


def test_the_mutation_escape_is_closed_end_to_end() -> None:
    # `__builtins__.clear()` used to run clean through every validator and
    # corrupt the interpreter.
    with pytest.raises(ValidationError, match="__builtins__ is forbidden"):
        Interpreter().run_source("__builtins__.clear()\n")
