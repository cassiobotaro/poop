from typing import ClassVar

from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import false, true


class _Wrapper(_ValueEqMixin):
    _eq_attr: ClassVar[str] = "_value"

    def __init__(self, value: int) -> None:
        self._value = value


class _OtherWrapper(_ValueEqMixin):
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
