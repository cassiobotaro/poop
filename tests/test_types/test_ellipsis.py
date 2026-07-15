from poop.types.boolean import false, true
from poop.types.ellipsis import EllipsisClass, ellipsis
from poop.types.ellipsis import ellipsis as ellipsis2
from poop.types.string import Str


def test_ellipsis_is_instance_of_ellipsis_class() -> None:
    assert isinstance(ellipsis, EllipsisClass)


def test_ellipsis_is_singleton() -> None:
    assert ellipsis is ellipsis2


def test_str_matches_python() -> None:
    assert str(ellipsis) == str(...)


def test_repr_delegates_to_str() -> None:
    assert repr(ellipsis) == "Ellipsis"


def test_is_truthy_like_python() -> None:
    assert bool(ellipsis) is bool(...)


def test_is_none_returns_false() -> None:
    assert ellipsis.is_none() is false


def test_not_none_returns_true() -> None:
    assert ellipsis.not_none() is true


def test_class_name_answers_python_type_name() -> None:
    name = ellipsis.class_name()
    assert isinstance(name, Str)
    assert str(name) == type(...).__name__


def test_class_passes_as_the_python_builtin() -> None:
    assert EllipsisClass.__module__ == "builtins"
    assert repr(EllipsisClass) == repr(type(...))
