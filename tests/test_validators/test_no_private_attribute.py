"""The third spelling of reaching into an object, and the one a reader types.

`get_attr("_value")` was refused and `obj._value` was not, so the guarded
spelling was the only guarded spelling — and the open one handed back a naked
Python primitive that answered nothing in POOP's vocabulary.
"""

import pytest

from poop.errors import PoopError, ValidationError
from poop.interpreter import Interpreter
from poop.validators.no_private_attribute import NoPrivateAttributeValidator


def _errors(source: str) -> list[ValidationError]:
    return Interpreter().validate_all(source)


@pytest.mark.parametrize(
    "source",
    [
        '"abc"._value',
        "[1, 2]._items",
        '{"a": 1}._data',
        "x = 5\nx._value",
        'other = "abc"\nother._value.print()',
        "class C(Object):\n    pass\nc = C()\nd = C()\nd._x",
    ],
)
def test_a_private_attribute_is_refused(source: str) -> None:
    with pytest.raises(PoopError, match="leading underscore"):
        Interpreter().run_source(source + "\n")


def test_the_refusal_names_the_substitute() -> None:
    errors = _errors('"abc"._value\n')
    assert len(errors) == 1
    assert "obj.get_attr(name)" in str(errors[0])


@pytest.mark.parametrize(
    "source",
    [
        # `self` — an object reaching its own state is not reaching into
        # anything, and `self._balance = balance` is how a POOP object holds it.
        "class C(Object):\n"
        "    def init(self, v):\n"
        "        self._v = v\n"
        "        return self\n"
        "    def v(self):\n"
        "        return self._v\n"
        "C().init(7).v().print()\n",
        # `cls`, for a classmethod.
        "class C(Object):\n"
        "    _default = 9\n"
        "    @classmethod\n"
        "    def make(cls):\n"
        "        return cls._default\n"
        "C.make().print()\n",
        # The enclosing class by its own name — the one allowance the rule
        # costs, for a `@staticmethod` with neither `self` nor `cls` to write.
        "class C(Object):\n"
        "    _secret = 5\n"
        "    @staticmethod\n"
        "    def helper():\n"
        "        return C._secret\n"
        "C.helper().print()\n",
    ],
    ids=["self", "cls", "own-class-by-name"],
)
def test_an_object_reaching_its_own_state_is_allowed(source: str) -> None:
    Interpreter().run_source(source)


def test_a_dunder_is_left_to_its_own_validator() -> None:
    # Refusing it here too would answer two sentences for one spelling.
    errors = NoPrivateAttributeValidator().collect(
        __import__("ast").parse("x.__class__\n")
    )
    assert errors == []


def test_a_poop_prefix_is_left_to_its_own_validator() -> None:
    # `no_poop_prefix` reserves the whole family and says why; this one would
    # only add a second sentence about the same name.
    messages = [str(e) for e in _errors("x._poop_int\n")]
    assert any("_poop_" in m for m in messages)
    assert not any("leading underscore" in m for m in messages)


def test_every_occurrence_is_reported() -> None:
    # `collect` is the primitive, which is what `--validators-only` needs.
    assert len(_errors('"a"._value\n"b"._value\n"c"._value\n')) == 3


def test_the_examples_corpus_is_clean() -> None:
    # The sweep the proposal promised: one allowance, no rewrites.
    import pathlib

    root = pathlib.Path(__file__).parent.parent.parent / "examples"
    offenders = [
        path.name
        for path in sorted(root.rglob("*.py"))
        if any(
            "leading underscore" in str(error)
            for error in _errors(path.read_text(encoding="utf-8"))
        )
    ]
    assert offenders == []
