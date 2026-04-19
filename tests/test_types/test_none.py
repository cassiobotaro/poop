from poop.types.boolean import false, true
from poop.types.none import NoneClass, none


def test_none_is_instance_of_none_class() -> None:
    assert isinstance(none, NoneClass)


def test_none_is_singleton() -> None:
    from poop.types.none import none as none2

    assert none is none2


def test_is_none_returns_true() -> None:
    assert none.is_none() is true


def test_not_none_returns_false() -> None:
    assert none.not_none() is false


def test_object_is_none_returns_false() -> None:
    from poop.types.object import Object

    assert Object().is_none() is false


def test_object_not_none_returns_true() -> None:
    from poop.types.object import Object

    assert Object().not_none() is true


def test_str_none() -> None:
    assert str(none) == "None"


def test_repr_delegates_to_str() -> None:
    assert repr(none) == str(none)


def test_bool_none_is_false() -> None:
    assert bool(none) is False


def test_class_name() -> None:
    assert none.class_name() == "NoneClass"
