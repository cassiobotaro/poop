"""`Object` has no instance-side hooks; messages are descriptors.

`Object.__getattribute__` wrapped a public bound method in a `_MethodBlock`
and `Object.__setattr__` reworded the `no __dict__` refusal; both were Python
frames on every attribute read and every object construction in the language.
The first job moved to the `message` descriptor `PoopMeta.__new__` installs,
the second to `poop_message`. This pins that neither hook comes back and that
every read answers what it answered.
"""

from types import FunctionType

import pytest

from poop.types._descriptor import message
from poop.types._message import poop_message
from poop.types._selectors import is_message
from poop.types.block import _MethodBlock
from poop.types.boolean import true
from poop.types.int import Int
from poop.types.list import List
from poop.types.object import Object
from poop.types.string import Str
from tests.test_no_python_wording import _receivers


def test_object_defines_neither_instance_side_hook() -> None:
    assert "__getattribute__" not in vars(Object)
    assert "__setattr__" not in vars(Object)


def _entry(receiver: object, name: str) -> object:
    for klass in type(receiver).__mro__:
        if name in vars(klass):
            return vars(klass)[name]
    raise AssertionError(name)


def test_every_public_method_read_off_a_value_is_a_block() -> None:
    # The same test the hook made: a method or classmethod binds to a
    # `MethodType` and wraps; a staticmethod binds to a plain function and
    # stays native, as it did before.
    for receiver in _receivers().values():
        for name in dir(receiver):
            if not is_message(name):
                continue
            entry = _entry(receiver, name)
            if not isinstance(entry, message):
                continue
            value = getattr(receiver, name)
            if isinstance(entry._entry, staticmethod):
                assert isinstance(value, FunctionType), name
            else:
                assert isinstance(value, _MethodBlock), (type(receiver).__name__, name)


def test_a_classmethod_read_off_an_instance_still_wraps() -> None:
    assert isinstance(Int(5).from_bytes, _MethodBlock)
    assert repr(Int(5).from_bytes) == "<block>"


def test_a_staticmethod_read_off_an_instance_stays_native_as_before() -> None:
    assert isinstance(Str("").maketrans, FunctionType)


def test_a_user_class_method_is_a_block_and_super_still_binds() -> None:
    class Base(Object):
        def greet(self) -> Str:
            return Str("hi")

    class Child(Base):
        def greet(self) -> Str:
            return super().greet() + Str("!")

    assert isinstance(Child().greet, _MethodBlock)
    assert repr(Child().greet) == "<block>"
    assert Child().greet() == Str("hi!")


def test_a_block_held_as_state_still_reads_back_as_itself() -> None:
    class Holder(Object):
        pass

    holder = Holder()
    holder.set_attr(Str("callback"), lambda: Int(1))
    assert not isinstance(holder.get_attr(Str("callback")), _MethodBlock)


def test_private_and_dunder_reads_are_not_wrapped() -> None:
    assert isinstance(Int(5)._value, int)
    assert type(Int(5).__eq__).__name__ == "method"


def test_the_class_side_still_refuses_an_instance_method() -> None:
    with pytest.raises(AttributeError, match="#upper asks an instance; send it to one"):
        Str.upper()  # ty: ignore[missing-argument] — the refusal is the point


def test_the_assignment_refusal_reads_the_same_words_both_ways() -> None:
    try:
        Str("abc").x = 5  # type: ignore[unresolved-attribute]
    except AttributeError as exc:
        assigned = poop_message(exc)
    with pytest.raises(AttributeError) as info:
        Str("abc").set_attr(Str("x"), Int(5))
    assert assigned == str(info.value)
    assert assigned == (
        "str is a value — it holds no state of its own; "
        "only an object of a class you defined can be given one"
    )


def test_a_message_still_calls_and_compares_as_before() -> None:
    xs = List(Int(1), Int(2))
    assert xs.len() == Int(2)
    assert xs.len == xs.len
    assert (xs.len != xs.at) is true
