from poop.types.boolean import false, true
from poop.types.object import Object


def test_is_none_returns_false() -> None:
    assert Object().is_none() is false


def test_not_none_returns_true() -> None:
    assert Object().not_none() is true


def test_not_truthy_object_returns_false() -> None:
    class Truthy(Object):
        def __bool__(self) -> bool:
            return True

    assert Truthy().not_() is false


def test_not_falsy_object_returns_true() -> None:
    class Falsy(Object):
        def __bool__(self) -> bool:
            return False

    assert Falsy().not_() is true


def test_class_name_returns_type_name() -> None:
    from poop.types.string import Str

    assert Object().class_name() == Str("Object")


def test_responds_to_existing_method() -> None:
    assert Object().responds_to("class_name") is true


def test_responds_to_missing_method() -> None:
    assert Object().responds_to("nonexistent") is false


def test_id_returns_int() -> None:
    from poop.types.int import Int

    obj = Object()
    result = obj.id()
    assert isinstance(result, Int)
    assert result == Int(id(obj))


def test_hash_returns_int() -> None:
    from poop.types.int import Int

    obj = Object()
    result = obj.hash()
    assert isinstance(result, Int)
    assert result == Int(hash(obj))


def test_str_default() -> None:
    assert str(Object()) == "<Object>"


def test_repr_delegates_to_str() -> None:
    obj = Object()
    assert repr(obj) == str(obj)
