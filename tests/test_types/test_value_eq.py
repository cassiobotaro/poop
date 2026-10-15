from typing import ClassVar

import pytest

from poop.interpreter import Interpreter
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import false, true
from poop.types.object import Object


# Each fixture inherits `Object` as every real user of the mixin does: the
# mixin owns `__eq__`, and `__ne__` is `Object`'s negation of it.
class _Wrapper(_ValueEqMixin, Object):
    _eq_attr: ClassVar[str] = "_value"

    def __init__(self, value: int) -> None:
        self._value = value


class _OtherWrapper(_ValueEqMixin, Object):
    _eq_attr: ClassVar[str] = "_value"

    def __init__(self, value: int) -> None:
        self._value = value


def test_eq_returns_true_when_attr_matches() -> None:
    assert _Wrapper(1).__eq__(_Wrapper(1)) is true


def test_eq_returns_false_when_attr_differs() -> None:
    assert _Wrapper(1).__eq__(_Wrapper(2)) is false


def test_eq_returns_false_against_different_type() -> None:
    assert _Wrapper(1).__eq__(_OtherWrapper(1)) is false


def test_eq_returns_false_against_unrelated_object() -> None:
    assert _Wrapper(1).__eq__("not a wrapper") is false


def test_ne_returns_false_when_attr_matches() -> None:
    assert _Wrapper(1).__ne__(_Wrapper(1)) is false


def test_ne_returns_true_when_attr_differs() -> None:
    assert _Wrapper(1).__ne__(_Wrapper(2)) is true


def test_ne_returns_true_against_different_type() -> None:
    assert _Wrapper(1).__ne__(_OtherWrapper(1)) is true


def test_eq_attr_is_configurable_per_subclass() -> None:
    class _ItemsWrapper(_ValueEqMixin):
        _eq_attr: ClassVar[str] = "_items"

        def __init__(self, items: tuple[int, ...]) -> None:
            self._items = items

    assert _ItemsWrapper((1, 2)).__eq__(_ItemsWrapper((1, 2))) is true
    assert _ItemsWrapper((1, 2)).__eq__(_ItemsWrapper((1, 3))) is false


# A program's subclass of a wrapper: CPython calls the right operand's `__eq__`
# first when its class is a subclass of the left's, so the subclass's test ran
# with the base on the other side and answered `false` — final, not
# `NotImplemented` — in both operand orders.


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ('class Name(str):\n    pass\n(Name("a") == "a").print()', "True"),
        ('class Name(str):\n    pass\n("a" == Name("a")).print()', "True"),
        ("class Stack(list):\n    pass\n(Stack([1]) == [1]).print()", "True"),
        ('class Name(str):\n    pass\n{Name("a"): 1}.at("a").print()', "1"),
        ('class Name(str):\n    pass\n(Name("a") == "b").print()', "False"),
    ],
    ids=["subclass_left", "subclass_right", "list_subclass", "dict_lookup", "unequal"],
)
def test_a_subclass_of_a_wrapper_equals_the_wrapper_by_value(
    source: str, expected: str, capsys: pytest.CaptureFixture[str]
) -> None:
    Interpreter().run_source(source)
    assert capsys.readouterr().out.strip() == expected


def test_a_subclass_instance_compares_equal_from_either_side() -> None:
    class _Sub(_Wrapper):
        pass

    assert _Wrapper(1).__eq__(_Sub(1)) is true
    assert _Sub(1).__eq__(_Wrapper(1)) is true
    assert _Sub(1).__eq__(_Wrapper(2)) is false
