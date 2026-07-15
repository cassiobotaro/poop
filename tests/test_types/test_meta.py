from abc import ABC

import pytest

from poop.types.boolean import Boolean, false, true
from poop.types.int import Int
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
