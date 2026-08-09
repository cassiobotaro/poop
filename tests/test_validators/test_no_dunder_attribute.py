import ast
import re
from collections.abc import Callable

import pytest

from poop.errors import ValidationError
from poop.interpreter import Interpreter
from poop.types.int import Int
from poop.types.string import Str
from poop.validators.no_dunder_attribute import (
    NoDunderAttributeValidator,
    dunder_message,
)


def _validate(source: str) -> None:
    NoDunderAttributeValidator().validate(ast.parse(source))


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("x.__dict__", "vars(obj) by another spelling"),
        ("x.__class__", "obj.class_()"),
        ("x.__name__", "Klass.name()"),
        ("x.__mro__", "Klass.superclass()"),
        ("x.__bases__", "Klass.superclass()"),
        ("x.__len__()", "obj.len()"),
        ("x.__contains__(1)", "col.includes(x)"),
        ("x.__abs__()", "n.abs()"),
        ("x.__hash__()", "obj.hash()"),
    ],
)
def test_forbidden_dunders_name_their_substitute(source: str, expected: str) -> None:
    with pytest.raises(ValidationError, match=re.escape(expected)):
        _validate(source)


def test_the_ban_is_a_rule_not_a_list() -> None:
    # An enumerated ban was already incomplete on paper: `__class__.__name__`
    # answers a raw `str`, and nobody had listed `__name__`.
    with pytest.raises(ValidationError, match="dunders are Python's protocol"):
        _validate("x.__frobnicate__")


def test_init_is_carved_out_for_super() -> None:
    # INFECTIONS.md allows `super` explicitly — without it inheritance breaks
    # entirely, and there is no message-passing substitute.
    _validate("class C:\n    def __init__(self):\n        super().__init__()\n")


@pytest.mark.parametrize(
    "source",
    [
        's = "abc"\ns.__init__("zap")',
        "n = 5\nn.__init__(99)",
        "t = (1, 2)\nt.__init__(9)",
        "obj.__init__()",
        "self.__init__()",
        "super.__init__()",
    ],
)
def test_init_is_refused_on_any_other_receiver(source: str) -> None:
    # The carve-out is for the `super().__init__(...)` *syntax*, not for the
    # name: applied to the name it re-ran the constructor on a live value, so
    # `Str`, `Int` and `Tuple` were all mutable and a `Dict` keyed on one held
    # an entry reachable under neither the old spelling nor the new.
    with pytest.raises(ValidationError, match="__init__ is forbidden"):
        _validate(source)


def test_a_plain_message_is_untouched() -> None:
    _validate("x.len()")
    _validate("x.class_()")


def test_a_single_underscore_name_is_untouched() -> None:
    _validate("x._private")


def test_super_init_still_runs_end_to_end() -> None:
    Interpreter().run_source(
        "class Animal:\n"
        "    def __init__(self, name):\n"
        "        self.name = name\n"
        "class Dog(Animal):\n"
        "    def __init__(self, name):\n"
        "        super().__init__(name)\n"
        'Dog("Rex")\n'
    )


def test_every_occurrence_is_reported() -> None:
    # Collecting, per proposal 10.
    errors = Interpreter().validate_all(
        "class C:\n    def m(self):\n        x.__len__()\n        y.__mro__\n"
    )
    dunder = [e for e in errors if "forbidden" in e.args[0] and "." in e.args[0][:2]]
    assert len(dunder) == 2


# --- the runtime guard: the half no validator can reach ---


def test_get_attr_rejects_a_dunder() -> None:
    with pytest.raises(
        AttributeError, match=re.escape("vars(obj) by another spelling")
    ):
        Int(5).get_attr(Str("__dict__"))


def test_get_attr_rejects_a_computed_dunder_name() -> None:
    # The whole reason the guard exists: no static validator can see this.
    with pytest.raises(AttributeError, match="forbidden"):
        Int(5).get_attr(Str("__dict" + "__"))


def test_get_attr_default_does_not_soften_the_ban() -> None:
    # A forbidden name is refused, not quietly answered with the fallback.
    with pytest.raises(AttributeError, match="forbidden"):
        Int(5).get_attr(Str("__dict__"), "fallback")


def test_has_attr_rejects_a_dunder() -> None:
    with pytest.raises(AttributeError, match="forbidden"):
        Int(5).has_attr(Str("__class__"))


def test_set_attr_rejects_a_dunder() -> None:
    with pytest.raises(AttributeError, match="forbidden"):
        Int(5).set_attr(Str("__class__"), 1)


def test_del_attr_rejects_a_dunder() -> None:
    with pytest.raises(AttributeError, match="forbidden"):
        Int(5).del_attr(Str("__class__"))


@pytest.mark.parametrize(
    "send",
    [
        lambda: Int(5).get_attr(Str("__init__")),
        lambda: Int(5).has_attr(Str("__init__")),
        lambda: Int(5).set_attr(Str("__init__"), 1),
        lambda: Int(5).del_attr(Str("__init__")),
    ],
    ids=["get_attr", "has_attr", "set_attr", "del_attr"],
)
def test_the_guard_refuses_init(send: Callable[[], object]) -> None:
    # The validator's carve-out is for `super().__init__(...)`, a *syntax* —
    # these four are not it, and inheriting the exemption made every immutable
    # wrapper mutable: `s.get_attr("__init__")("ZAP")` re-ran the constructor
    # on a live Str, and a Dict keyed on one lost the entry.
    with pytest.raises(AttributeError, match="__init__ is forbidden"):
        send()


def test_the_validator_still_allows_init() -> None:
    # The other half of the same ban: `super().__init__(...)` must still parse,
    # or inheritance breaks entirely.
    assert dunder_message("__init__") is None
    NoDunderAttributeValidator().validate(
        ast.parse("class C:\n    def m(self):\n        super().__init__()")
    )


def test_the_guard_leaves_ordinary_names_alone() -> None:
    assert Int(5).has_attr(Str("abs"))
    assert Int(5).get_attr(Str("nope"), "fallback") == "fallback"
