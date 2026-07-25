from abc import ABC
from typing import Any

import pytest

from poop.errors import ValidationError
from poop.interpreter import Interpreter
from poop.types.boolean import Boolean, false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.meta import PoopMeta
from poop.types.none import none
from poop.types.object import MessageNotUnderstood, Object
from poop.types.string import Str


class _Animal(Object):
    __slots__ = ()

    def speak(self) -> Str:
        return Str("...")


class _Dog(_Animal):
    __slots__ = ()

    def speak(self) -> Str:
        return Str("woof")


def test_a_class_answers_print_instead_of_failing_to_bind() -> None:
    # `Foo.print()` used to answer "Object.print() missing 1 required
    # positional argument: 'self'" — Python failing to bind, not POOP refusing.
    _Dog.print()


def test_a_class_answers_its_name() -> None:
    assert _Dog.name() == Str("_Dog")


def test_a_class_answers_its_superclass_as_a_class_not_a_name() -> None:
    assert _Dog.superclass() is _Animal
    assert _Dog.superclass().name() == Str("_Animal")


def test_the_root_answers_none_for_superclass() -> None:
    # Smalltalk answers nil for `Object superclass`, which also keeps the raw
    # Python `object` underneath out of reach.
    assert Object.superclass() is none


def test_a_class_answers_has_attr() -> None:
    assert _Dog.has_attr(Str("speak")) is true
    assert _Dog.has_attr(Str("fly")) is false


def test_a_class_has_attr_rejects_private_and_dunder() -> None:
    # The class side must guard like the instance side, not answer freely.
    with pytest.raises(AttributeError, match="private"):
        _Dog.has_attr(Str("_data"))
    with pytest.raises(AttributeError):
        _Dog.has_attr(Str("__dict__"))


def test_a_class_get_attr_rejects_a_private_name() -> None:
    with pytest.raises(AttributeError, match="private"):
        _Dog.get_attr(Str("_data"))


def test_instances_still_get_the_instance_side() -> None:
    # The metaclass must not shadow instance messages: lookup on an instance
    # never consults the metaclass.
    assert _Dog().speak() == Str("woof")
    assert isinstance(_Dog().has_attr(Str("speak")), Boolean)


def test_class_side_wins_over_a_same_named_instance_method() -> None:
    # `Object.print` sits in _Dog's MRO, which is searched before the
    # metaclass. Only a data descriptor is consulted first — this asserts the
    # class side is one.
    class _Named(Object):
        __slots__ = ()

        def name(self) -> Str:
            return Str("instance name")

    assert _Named.name() == Str("_Named")
    assert _Named().name() == Str("instance name")


def test_class_answers_the_class_object_itself() -> None:
    assert Int(5).class_() is Int


def test_class_name_is_the_class_answering_its_own_name() -> None:
    assert Int(5).class_name() == Int.name()
    assert Int(5).class_name() == Str("int")


def test_unknown_message_to_a_class_speaks_smalltalk_too() -> None:
    # Instances got doesNotUnderstand first; classes answered Python's
    # "type object 'Foo' has no attribute 'frobnicate'" until the metaclass
    # carried the hook.
    with pytest.raises(MessageNotUnderstood, match="_Dog does not understand"):
        _Dog.frobnicate()  # ty: ignore[unresolved-attribute]


def test_unknown_message_to_a_class_maps_smalltalk_selectors() -> None:
    with pytest.raises(MessageNotUnderstood, match="#printNl is #print here"):
        _Dog.printNl()  # ty: ignore[unresolved-attribute]


def test_a_class_gets_no_selector_hint_it_cannot_honour() -> None:
    # `size` maps to `len`, which a class does not answer — do not promise it.
    with pytest.raises(MessageNotUnderstood, match=":methods"):
        _Dog.size()  # ty: ignore[unresolved-attribute]


def test_poop_meta_derives_from_abcmeta() -> None:
    # `Boolean(Object, ABC)` fails with a metaclass conflict otherwise.
    assert issubclass(PoopMeta, type(ABC))


def test_an_abstract_poop_class_still_builds() -> None:
    class _Abstract(Object, ABC):
        __slots__ = ()

    assert _Abstract.name() == Str("_Abstract")


def test_the_metaclass_propagates_without_being_declared() -> None:
    # ClassTransformer routes every user class through Object, so nothing has
    # to name PoopMeta for a class to answer.
    assert isinstance(_Dog, PoopMeta)
    assert isinstance(Int, PoopMeta)


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("is_none", false),
        ("not_none", true),
        ("not_", false),
        ("callable", true),
    ],
)
def test_a_class_answers_the_boolean_protocol(message: str, expected: Boolean) -> None:
    assert getattr(_Dog, message)() is expected


def test_a_class_answers_hash_and_id_as_ints() -> None:
    # `hash(Foo)` answers "hash() is forbidden — use obj.hash() instead" while
    # `Foo.hash()` answered a binding error: the ban named a substitute that
    # did not exist on that receiver.
    assert _Dog.hash() == Int(hash(_Dog))
    assert _Dog.id() == Int(id(_Dog))


def test_a_class_reprs_as_its_name_like_print_does() -> None:
    # Not builtins.repr(cls), which answers `<class 'builtins._Dog'>` — Python's
    # vocabulary inside a POOP message's answer.
    assert _Dog.repr() == Str("_Dog")
    assert _Dog.ascii() == Str("_Dog")


def test_a_class_ascii_escapes_a_non_ascii_name() -> None:
    class Ação(Object):  # noqa: N801
        __slots__ = ()

    assert Ação.repr() == Str("Ação")
    assert Ação.ascii() == Str("A\\xe7\\xe3o")


def test_a_class_answers_dir_as_poop_strings() -> None:
    names = _Dog.dir()
    assert isinstance(names, List)
    assert all(isinstance(n, Str) for n in names._items)


def test_a_class_answers_format() -> None:
    assert _Dog.format() == Str("_Dog")
    assert _Dog.format(Str(">6")) == Str("  _Dog")


def test_a_class_refuses_class_and_class_name_naming_the_right_message() -> None:
    # Smalltalk answers the metaclass here; POOP has none to answer with, since
    # PoopMeta is not itself a POOP class. Answering `_Dog` would make
    # class_name mean one thing on an instance and another on a class.
    for message in ("class_", "class_name"):
        with pytest.raises(MessageNotUnderstood, match="a class answers #name"):
            getattr(_Dog, message)()


def test_poop_meta_is_not_itself_a_poop_class() -> None:
    # Which is why class_() cannot answer it: it would leak the raw class
    # object the class side exists to remove.
    assert not isinstance(PoopMeta, PoopMeta)


def test_instances_keep_the_instance_side_for_all_of_them() -> None:
    dog = _Dog()
    assert dog.class_() is _Dog
    assert dog.class_name() == Str("_Dog")
    assert dog.is_none() is false
    assert isinstance(dog.hash(), Int)


def test_a_class_answers_identity() -> None:
    # `Foo is Bar` is banned (no_is); `Foo.is_identical(Bar)` is the substitute
    # and answered a binding error until now.
    assert _Dog.is_identical(_Dog) is true
    assert _Dog.is_identical(_Animal) is false
    assert _Dog.not_identical(_Animal) is true


def test_a_class_answers_is_instance() -> None:
    # A class is an instance of its metaclass, not of its bases — so a class is
    # not an instance of Object, though it is a subclass of it.
    assert _Dog.is_instance(PoopMeta) is true
    assert _Dog.is_instance(Object) is false
    assert _Dog.is_subclass(Object) is true


def test_a_class_answers_the_none_protocol_as_never_none() -> None:
    assert _Dog.if_none(lambda: 0) is _Dog
    assert _Dog.if_not_none(lambda c: c.name()) == Str("_Dog")


def test_a_class_assert_always_holds() -> None:
    # A class is always truthy, so assert_ answers the class.
    assert _Dog.assert_() is _Dog


def test_a_class_answers_attribute_access() -> None:
    class _Box(Object):
        __slots__ = ()

    _Box.set_attr(Str("tag"), Int(7))
    assert _Box.get_attr(Str("tag")) == Int(7)
    assert _Box.has_attr(Str("tag")) is true
    _Box.del_attr(Str("tag"))
    assert _Box.has_attr(Str("tag")) is false


def test_class_side_attr_access_keeps_the_dunder_guard() -> None:
    # no_dunder_attribute's runtime half must hold on the class side too.
    for name in ("__dict__", "__class__"):
        with pytest.raises(AttributeError, match="forbidden"):
            _Dog.get_attr(Str(name))


def test_the_isinstance_ban_now_names_a_message_that_exists() -> None:
    # item 14's contradiction, for the last of the messages it missed:
    # `isinstance(Foo, T)` is banned and points at `Foo.is_instance(T)`.
    with pytest.raises(ValidationError, match="obj.is_instance"):
        Interpreter().run_source(
            "class Foo:\n    def m(self):\n        isinstance(Foo, Foo)\n"
        )
    assert _Dog.is_instance(Object) is false


def test_class_side_accessed_on_metaclass_returns_the_descriptor() -> None:
    # Reached via the metaclass itself (instance is None): the descriptor
    # answers itself rather than a bound partial.
    from poop.types.meta import PoopMeta, class_side

    assert isinstance(PoopMeta.__dict__["name"], class_side)
    assert PoopMeta.name is PoopMeta.__dict__["name"]


def test_class_side_message_cannot_be_reassigned() -> None:
    # A class-side name is a data descriptor; assigning over it on a class is
    # rejected rather than silently shadowing the message.
    from poop.types.object import Object

    class _Thing(Object):
        __slots__ = ()

    with pytest.raises(AttributeError):
        _Thing.name = 5


@pytest.mark.parametrize(
    "call",
    [
        pytest.param(lambda bad: _Dog.get_attr(bad), id="get_attr"),
        pytest.param(lambda bad: _Dog.has_attr(bad), id="has_attr"),
        pytest.param(lambda bad: _Dog.set_attr(bad, Int(1)), id="set_attr"),
        pytest.param(lambda bad: _Dog.del_attr(bad), id="del_attr"),
    ],
)
def test_the_class_side_rejects_a_non_str_name_faithfully(call: Any) -> None:
    # One ban, one message: the class side leaked `#_value` for a non-Str name
    # exactly as the instance side did.
    bad: Any = List(Int(1))
    with pytest.raises(TypeError, match="attribute name must be string, not 'list'"):
        call(bad)
