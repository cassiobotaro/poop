import pytest

from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.object import Object
from poop.types.string import Str


def test_is_none_returns_false() -> None:
    assert Object().is_none() is false


def test_not_none_returns_true() -> None:
    assert Object().not_none() is true


def test_is_identical_same_object() -> None:
    obj = Object()
    assert obj.is_identical(obj) is true


def test_is_identical_distinct_objects() -> None:
    assert Object().is_identical(Object()) is false


def test_is_identical_value_equal_distinct() -> None:
    assert Int(1).is_identical(Int(1)) is false


def test_not_identical_same_object() -> None:
    obj = Object()
    assert obj.not_identical(obj) is false


def test_not_identical_distinct_objects() -> None:
    assert Object().not_identical(Object()) is true


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
    assert Object().class_name() == Str("object")


def test_has_attr_existing_method() -> None:
    assert Object().has_attr(Str("class_name")) is true


def test_has_attr_missing_method() -> None:
    assert Object().has_attr(Str("nonexistent")) is false


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
    obj = Object()
    result = obj.id()
    assert isinstance(result, Int)
    assert result == Int(id(obj))


def test_hash_returns_int() -> None:
    obj = Object()
    result = obj.hash()
    assert isinstance(result, Int)
    assert result == Int(hash(obj))


def test_get_attr_existing_attribute() -> None:
    result = Object().get_attr(Str("class_name"))
    assert callable(result)


def test_get_attr_missing_raises_attribute_error() -> None:
    with pytest.raises(AttributeError):
        Object().get_attr(Str("nonexistent"))


def test_get_attr_missing_with_default_returns_default() -> None:
    sentinel = object()
    result = Object().get_attr(Str("nonexistent"), sentinel)
    assert result is sentinel


def test_get_attr_rejects_a_private_name() -> None:
    # `_value` would hand back the raw Python primitive a POOP object wraps.
    with pytest.raises(AttributeError, match="private"):
        Int(42).get_attr(Str("_value"))


def test_get_attr_private_default_does_not_soften_the_ban() -> None:
    with pytest.raises(AttributeError, match="private"):
        Int(42).get_attr(Str("_value"), "fallback")


def test_has_attr_rejects_a_private_name() -> None:
    with pytest.raises(AttributeError, match="private"):
        List(Int(1)).has_attr(Str("_items"))


def test_set_attr_rejects_a_private_name() -> None:
    with pytest.raises(AttributeError, match="private"):
        Int(42).set_attr(Str("_value"), Int(99))


def test_set_attr_writes_to_declared_slot() -> None:
    from poop.types.none import none

    class Container(Object):
        __slots__ = ("data",)
        data: Int

    obj = Container()
    result = obj.set_attr(Str("data"), Int(42))
    assert obj.data == Int(42)
    assert result is none


def test_set_attr_on_unknown_slot_raises_attribute_error() -> None:
    with pytest.raises(AttributeError):
        Object().set_attr(Str("nonexistent"), Int(1))


def test_del_attr_removes_attribute() -> None:
    from poop.types.none import none

    class Container(Object):
        data: Int

    obj = Container()
    obj.data = Int(7)  # type: ignore[unresolved-attribute]
    result = obj.del_attr(Str("data"))
    assert not hasattr(obj, "data")
    assert result is none


def test_del_attr_missing_raises_attribute_error() -> None:
    with pytest.raises(AttributeError):
        Object().del_attr(Str("nonexistent"))


def test_repr_method_returns_str_type() -> None:
    result = Object().repr()
    assert isinstance(result, Str)


def test_repr_method_matches_builtin_repr() -> None:
    obj = Object()
    assert obj.repr() == Str(repr(obj))


def test_repr_method_custom_str() -> None:
    class Named(Object):
        def __str__(self) -> str:
            return "Named!"

    assert Named().repr() == Str("Named!")


def test_ascii_returns_str_type() -> None:
    result = Object().ascii()
    assert isinstance(result, Str)


def test_ascii_ascii_only_object() -> None:
    result = Object().ascii()
    assert result == Str("<object>")


def test_ascii_escapes_non_ascii_chars() -> None:
    class Exotic(Object):
        def __str__(self) -> str:
            return "café"

    result = Exotic().ascii()
    assert result == Str("caf\\xe9")


def test_format_without_spec_returns_str() -> None:
    result = Int(42).format()
    assert isinstance(result, Str)
    assert result == Str("42")


def test_format_int_with_hex_spec() -> None:
    from poop.types.float import Float

    assert Int(42).format(Str("x")) == Str("2a")
    assert Float(3.14159).format(Str(".2f")) == Str("3.14")
    # Str overrides Object.format with str.format template semantics
    # (proposal 151), so the "apply a spec to a string" case is written
    # via the template form instead of Str("abc").format(Str(">5")).
    assert Str("{:>5}").format(Str("abc")) == Str("  abc")


def test_format_invalid_spec_raises_value_error() -> None:
    with pytest.raises(ValueError):
        Int(42).format(Str("?invalid"))


def test_format_with_poop_none_treats_as_no_spec() -> None:
    from poop.types.none import none

    assert Int(42).format(none) == Str("42")


def test_print_accepts_poop_none_for_end(capsys: pytest.CaptureFixture[str]) -> None:
    from poop.types.none import none

    Int(7).print(end=none)
    captured = capsys.readouterr()
    assert captured.out == "7\n"


def test_print_accepts_poop_none_for_flush(capsys: pytest.CaptureFixture[str]) -> None:
    from poop.types.none import none

    Int(7).print(flush=none)
    captured = capsys.readouterr()
    assert captured.out == "7\n"


def test_dir_returns_list_of_str() -> None:
    result = Object().dir()
    assert isinstance(result, List)
    assert all(isinstance(item, Str) for item in result._items)


def test_dir_contains_known_method() -> None:
    result = Object().dir()
    assert Str("class_name") in result._items


def test_dir_hides_private_and_dunder_names() -> None:
    # The introspection substitute must not surface `_`-prefixed internals —
    # dunders or privates (including the mangled `_poop_*` bindings).
    result = Object().dir()
    assert all(not str(name).startswith("_") for name in result._items)


def test_str_default() -> None:
    assert str(Object()) == "<object>"


def test_repr_delegates_to_str() -> None:
    obj = Object()
    assert repr(obj) == str(obj)


def test_eq_same_object_returns_true() -> None:
    obj = Object()
    assert obj == obj
    result = obj.__eq__(obj)
    assert result is true


def test_eq_different_objects_returns_false() -> None:
    a, b = Object(), Object()
    result = a.__eq__(b)
    assert result is false


def test_ne_same_object_returns_false() -> None:
    obj = Object()
    result = obj.__ne__(obj)
    assert result is false


def test_ne_different_objects_returns_true() -> None:
    a, b = Object(), Object()
    result = a.__ne__(b)
    assert result is true
