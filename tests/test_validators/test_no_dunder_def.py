import ast
import inspect

import pytest

from poop.errors import ValidationError
from poop.validators.no_dunder_def import _REFUSED, NoDunderDefValidator


def _errors(source: str) -> list[ValidationError]:
    return NoDunderDefValidator().collect(ast.parse(source))


def _class_defining(name: str) -> str:
    return f"class P:\n    def {name}(self, *args):\n        return 1"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        (
            "__getattribute__",
            "defining __getattribute__ is forbidden — it is Python's lookup "
            "protocol; define does_not_understand(self, name) for the messages "
            "the class does not answer",
        ),
        (
            "__getattr__",
            "defining __getattr__ is forbidden — define does_not_understand(self, name) instead",
        ),
        (
            "__init_subclass__",
            "defining __init_subclass__ is forbidden — a class is built from its bases alone",
        ),
        (
            "__set_name__",
            "defining __set_name__ is forbidden — a POOP object is reached by "
            "messages, not by descriptors",
        ),
    ],
)
def test_a_refused_dunder_names_its_substitute(name: str, expected: str) -> None:
    (error,) = _errors(_class_defining(name))
    assert error.message == expected


@pytest.mark.parametrize("name", sorted(_REFUSED))
def test_every_deny_list_row_is_refused(name: str) -> None:
    (error,) = _errors(_class_defining(name))
    assert error.message.startswith(f"defining {name} is forbidden — ")
    assert error.lineno == 2


# The slots INFECTIONS.md documents as the ones a class may satisfy.
_LEGAL = (
    "__init__",
    "__str__",
    "__repr__",
    "__bool__",
    "__hash__",
    "__len__",
    "__call__",
    "__iter__",
    "__next__",
    "__enter__",
    "__exit__",
    "__eq__",
    "__lt__",
    "__add__",
    "__radd__",
    "__iadd__",
    "__neg__",
)


@pytest.mark.parametrize("name", _LEGAL)
def test_a_protocol_slot_stays_legal(name: str) -> None:
    assert _errors(_class_defining(name)) == []


# Dunders of `object` that are routines but neither refused nor in the legal
# list above: the pickle protocol, `format`, the remaining comparisons. A
# class defining one gains nothing a message cannot do, and loses nothing.
_HARMLESS = {
    "__format__",
    "__getstate__",
    "__reduce__",
    "__reduce_ex__",
    "__sizeof__",
    "__ne__",
    "__le__",
    "__gt__",
    "__ge__",
}


@pytest.mark.parametrize(
    "name",
    sorted(name for name in dir(object) if inspect.isroutine(getattr(object, name))),
)
def test_every_routine_dunder_of_object_is_accounted_for(name: str) -> None:
    # A callable dunder CPython's `object` carries is on the deny-list, in the
    # documented legal set, or named harmless above. A new one in a future
    # CPython lands here, and whoever adds it decides which list it joins.
    assert name in _REFUSED or name in _LEGAL or name in _HARMLESS, (
        f"{name} is a routine dunder no list accounts for"
    )


def test_a_free_function_is_not_a_class_body() -> None:
    assert _errors("def __getattr__(self, name):\n    return 1") == []


def test_validate_raises_the_first() -> None:
    with pytest.raises(ValidationError, match="defining __new__"):
        NoDunderDefValidator().validate(ast.parse(_class_defining("__new__")))
