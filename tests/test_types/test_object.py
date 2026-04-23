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


def test_has_attr_existing_method() -> None:
    assert Object().has_attr("class_name") is true


def test_has_attr_missing_method() -> None:
    assert Object().has_attr("nonexistent") is false


def test_is_instance_returns_true_for_matching_type() -> None:
    assert Object().is_instance(Object) is true


def test_is_instance_returns_false_for_non_matching_type() -> None:
    assert Object().is_instance(int) is false


def test_callable_returns_false_for_plain_object() -> None:
    assert Object().callable() is false


def test_callable_returns_true_for_callable_object() -> None:
    class CallableObj(Object):
        def __call__(self) -> None:
            pass

    assert CallableObj().callable() is true


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


def test_eq_same_object_returns_true() -> None:
    from poop.types.boolean import true

    obj = Object()
    assert obj == obj
    result = obj.__eq__(obj)
    assert result is true


def test_eq_different_objects_returns_false() -> None:
    from poop.types.boolean import false

    a, b = Object(), Object()
    result = a.__eq__(b)
    assert result is false


def test_ne_same_object_returns_false() -> None:
    from poop.types.boolean import false

    obj = Object()
    result = obj.__ne__(obj)
    assert result is false


def test_ne_different_objects_returns_true() -> None:
    from poop.types.boolean import true

    a, b = Object(), Object()
    result = a.__ne__(b)
    assert result is true


def test_on_error_returns_block_result_when_no_exception() -> None:
    from poop.types.int import Int

    obj = Object()
    result = obj.on_error(lambda: Int(42), ValueError, lambda e: Int(0))
    assert result == Int(42)


def test_on_error_calls_handler_when_exception_matches() -> None:
    from poop.types.string import Str

    obj = Object()
    result = obj.on_error(
        lambda: (_ for _ in ()).throw(ValueError("oops")),
        ValueError,
        lambda e: e.message(),
    )
    assert result == Str("oops")


def test_on_error_handler_receives_error_object() -> None:
    from poop.types.error import Error

    obj = Object()
    received: list[object] = []
    obj.on_error(
        lambda: (_ for _ in ()).throw(KeyError("k")),
        KeyError,
        lambda e: received.append(e),
    )
    assert len(received) == 1
    assert isinstance(received[0], Error)


def test_on_error_does_not_catch_unrelated_exception() -> None:
    import pytest

    obj = Object()
    with pytest.raises(TypeError):
        obj.on_error(
            lambda: (_ for _ in ()).throw(TypeError("wrong type")),
            ValueError,
            lambda e: None,
        )
