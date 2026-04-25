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


def test_is_subclass_returns_true_for_direct_subclass() -> None:
    class Animal(Object):
        pass

    class Dog(Animal):
        pass

    assert Dog.is_subclass(Animal) is true


def test_is_subclass_returns_false_for_unrelated_class() -> None:
    class A(Object):
        pass

    class B(Object):
        pass

    assert A.is_subclass(B) is false


def test_is_subclass_returns_true_for_self() -> None:
    class Foo(Object):
        pass

    assert Foo.is_subclass(Foo) is true


def test_is_subclass_returns_true_for_object_root() -> None:
    class Foo(Object):
        pass

    assert Foo.is_subclass(Object) is true


def test_is_subclass_via_instance_also_works() -> None:
    class Animal(Object):
        pass

    class Dog(Animal):
        pass

    assert Dog().is_subclass(Animal) is true


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


def test_ascii_returns_str_type() -> None:
    from poop.types.string import Str

    result = Object().ascii()
    assert isinstance(result, Str)


def test_ascii_ascii_only_object() -> None:
    from poop.types.string import Str

    result = Object().ascii()
    assert result == Str("<Object>")


def test_ascii_escapes_non_ascii_chars() -> None:
    from poop.types.string import Str

    class Exotic(Object):
        def __str__(self) -> str:
            return "café"

    result = Exotic().ascii()
    assert result == Str("caf\\xe9")


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
