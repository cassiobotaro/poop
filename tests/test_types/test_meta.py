from abc import ABC
from typing import Any

import pytest

from poop.errors import ExecutionError, ValidationError
from poop.interpreter import Interpreter
from poop.transformers import DEFAULT_NAMESPACE
from poop.types.boolean import Boolean, false, true
from poop.types.exceptions import MIRRORS
from poop.types.int import Int
from poop.types.list import List
from poop.types.meta import PoopMeta, class_side
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


class _Unrelated(Object):
    __slots__ = ()


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


def test_a_class_answers_hash_as_an_int() -> None:
    # `hash(Foo)` answers "hash() is forbidden — use obj.hash() instead" while
    # `Foo.hash()` answered a binding error: the ban named a substitute that
    # did not exist on that receiver.
    assert _Dog.hash() == Int(hash(_Dog))


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


def _dir(cls: Any) -> list[str]:
    """The messages `cls` lists, as plain strings.

    `Any`, not `PoopMeta`: `MIRRORS` is a `dict[str, type[Exception]]`, and a
    class object cannot be narrowed to the metaclass that answers `dir`.
    """
    return [str(name) for name in cls.dir()._items]


def test_a_class_lists_every_class_side_message_it_answers() -> None:
    # `type.__dir__` walks the class's own MRO only, so the whole class side
    # was reachable by typing and invisible to every discovery surface.
    answered = [
        name
        for name, attr in vars(PoopMeta).items()
        if isinstance(attr, class_side) and not attr.refuses
    ]
    listed = _dir(_Dog)
    assert set(answered) <= set(listed)
    # The two the merge exists for: no instance-side method spells either.
    assert "name" in listed
    assert "superclass" in listed


def test_a_class_does_not_list_the_messages_it_refuses() -> None:
    # Offering `mro` would name a message that answers "that is Python's".
    listed = _dir(_Dog)
    assert "mro" not in listed
    assert "register" not in listed


def test_a_class_lists_each_message_once() -> None:
    # The builtin `dir` sorts what `__dir__` answers but does not dedupe, so
    # every name `Object` also spells came back twice.
    listed = _dir(_Dog)
    assert len(listed) == len(set(listed))


def test_only_an_exception_class_lists_raise() -> None:
    # `raise_` is a message on `PoopExcMeta` and a refusal on `PoopMeta`, so
    # the merge has to resolve it per receiver, nearest metaclass first.
    assert "raise_" in _dir(MIRRORS["ValueError"])
    assert "raise_" not in _dir(_Dog)


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

    # And it says so: `AttributeError: name` read as if the *word* `name` were
    # the problem, and said neither what was refused nor why.
    with pytest.raises(AttributeError) as info:
        _Thing.name = 5
    assert str(info.value) == "#name is answered by every class — it cannot be rebound"


def test_the_set_attr_spelling_lands_on_the_same_sentence() -> None:
    # Both spellings of the mistake — the assignment and the sanctioned
    # substitute — reach `class_side.__set__`.
    from poop.types.object import Object
    from poop.types.string import Str

    class _Thing(Object):
        __slots__ = ()

    with pytest.raises(AttributeError, match="it cannot be rebound"):
        _Thing.set_attr(Str("name"), Int(5))


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


def test_the_class_side_answers_a_block_for_a_method() -> None:
    # Same wrap as the instance side; the unbound function takes its receiver
    # explicitly, as it does in Python.
    from poop.types.block import Block

    speak = _Dog.get_attr(Str("speak"))
    assert isinstance(speak, Block)
    assert speak(_Dog()) == Str("woof")


def test_the_class_side_leaves_a_poop_class_alone() -> None:
    # A class is callable but is already an object with its own protocol.
    assert _Dog.get_attr(Str("superclass"))() is _Animal


def test_a_class_refuses_mro_naming_superclass() -> None:
    # `type.mro` arrived with the metaclass and answered a raw Python list of
    # raw classes — `__mro__` under a spelling no_dunder_attribute cannot see,
    # holding the Python `object` that `superclass` stops short of on purpose.
    with pytest.raises(MessageNotUnderstood, match="a class answers #superclass"):
        _Dog.mro()


def test_refusing_mro_does_not_break_class_creation() -> None:
    # CPython calls the metaclass's `mro` to compute a new class's MRO, so an
    # unconditional refusal would break every `class` statement in the
    # language. Building a fresh subclass here is the regression test.
    class _Puppy(_Dog):
        __slots__ = ()

    assert _Puppy.superclass() is _Dog
    assert _Puppy().speak() == Str("woof")
    with pytest.raises(MessageNotUnderstood, match="a class answers #superclass"):
        _Puppy.mro()


def test_a_class_refuses_register_naming_is_subclass() -> None:
    # ABCMeta's virtual-subclass registration made `is_instance` answer true
    # for a class that never inherited from the receiver.
    with pytest.raises(MessageNotUnderstood, match="a class answers #is_subclass"):
        _Animal.register(_Unrelated)
    assert _Unrelated().is_instance(_Animal) is false


def test_neither_native_is_reachable_from_poop_source() -> None:
    # Both are invisible to `dir()` — `type.__dir__` does not merge the
    # metaclass's names — so nothing taught them and nothing stopped them.
    interpreter = Interpreter()
    for source in ("Object.mro()", "Object.register(Object)"):
        with pytest.raises(ExecutionError, match="is Python's"):
            interpreter.run_source(source)


def test_a_poop_builtin_refuses_to_have_its_messages_changed() -> None:
    # `__slots__` keeps state off the instance side; the class side had no
    # equivalent, so `class_()` was a route to rewriting the language.
    for cls in (Str, Int, List, Object):
        with pytest.raises(AttributeError, match="is a POOP builtin"):
            cls.set_attr(Str("zzz"), Int(1))
        with pytest.raises(AttributeError, match="is a POOP builtin"):
            cls.del_attr(Str("zzz"))


def test_a_mirror_refuses_too() -> None:
    # The mirrors are cloaked into `builtins` like every other wrapper.
    # `MIRRORS` is annotated `type[Exception]`, which knows nothing of the
    # class side, so the receiver is widened here rather than at the source.
    mirror: Any = MIRRORS["ValueError"]
    with pytest.raises(AttributeError, match="is a POOP builtin"):
        mirror.set_attr(Str("zzz"), Int(1))


def test_a_class_the_program_defined_still_takes_one() -> None:
    # The distinction is the one `Object.set_attr` already draws for
    # instances: only a class you defined can be given state.
    class _Crate(Object):
        __slots__ = ()

    _Crate.set_attr(Str("tag"), Int(7))
    assert _Crate.get_attr(Str("tag")) == Int(7)
    _Crate.del_attr(Str("tag"))
    assert _Crate.has_attr(Str("tag")) is false


def test_the_name_is_checked_before_the_receiver() -> None:
    # A forbidden *name* answers the ban it broke, on every receiver — the
    # builtin refusal must not swallow the dunder one.
    with pytest.raises(AttributeError, match="forbidden"):
        Str.set_attr(Str("__dict__"), Int(1))


def test_a_builtin_cannot_be_rewritten_from_poop_source() -> None:
    # The end-to-end spelling: `class_()` is the sanctioned way to reach a
    # class, and `no_getattr` names set_attr/del_attr as the substitutes.
    interpreter = Interpreter()
    for source in (
        '"abc".class_().del_attr("upper")',
        '(5).class_().set_attr("bit_length", lambda self: 1)',
    ):
        with pytest.raises(ExecutionError, match="is a POOP builtin"):
            interpreter.run_source(source)


# --- comparing two classes is a message, not a Python operator ---
#
# `Object.__eq__` answers a `Boolean`; a class is compared by its metaclass,
# and nothing defined the message there — so `int == int` handed a raw Python
# `bool` back to user code, which answered `'bool' object has no attribute
# 'print'`.


def test_class_equality_answers_a_poop_boolean() -> None:
    assert isinstance(_Dog == _Dog, Boolean)
    assert (_Dog == _Dog) is true
    assert (_Dog == _Animal) is false


def test_class_inequality_answers_a_poop_boolean() -> None:
    assert isinstance(_Dog != _Animal, Boolean)
    assert (_Dog != _Animal) is true
    assert (_Dog != _Dog) is false


def test_a_wrapper_equals_the_bare_name_that_spells_it() -> None:
    # `class_()` answers the wrapper, a bare `int` the alias built on it, so
    # `(5).class_() == int` was False for two objects that both say `int`.
    from poop.transformers.int import IntTransformer

    alias = IntTransformer.BINDINGS["_poop_int_cls"]
    assert (Int(5).class_() == alias) is true
    assert (alias == Int(5).class_()) is true


def test_a_class_compared_with_a_non_class_is_simply_unequal() -> None:
    assert (_Dog == Int(5)) is false
    assert (_Dog != Int(5)) is true


def test_identity_still_separates_the_wrapper_from_its_alias() -> None:
    # `is_identical` asks identity, and those really are two objects — the
    # question `==` answers is the other one.
    from poop.transformers.int import IntTransformer

    alias = IntTransformer.BINDINGS["_poop_int_cls"]
    assert Int(5).class_().is_identical(alias) is false


def test_a_poop_class_is_still_hashable() -> None:
    # Defining `__eq__` drops `__hash__`, and `NATIVE_TO_POOP` keys on classes.
    assert len({_Dog, _Animal, _Dog}) == 2


# --- the protocol slots a program is allowed to define ---
#
# A POOP method can only return POOP values, and CPython reads these slots
# itself and demands a native — so every one of them was unsatisfiable from
# inside the language, with a sentence that contradicted itself
# (`__str__ returned non-string (type str)`).


def _run(source: str) -> None:
    Interpreter().run_source(source)


def _printed(source: str, capsys: pytest.CaptureFixture[str]) -> str:
    _run(source)
    return capsys.readouterr().out.strip()


def test_a_user_class_can_define_how_it_prints(
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = (
        "class P(Object):\n"
        "    def __str__(self):\n"
        '        return "P!"\n'
        "P().print()\n"
        "str(P()).print()\n"
    )
    assert _printed(source, capsys) == "P!\nP!"


def test_a_user_class_can_define_its_repr(capsys: pytest.CaptureFixture[str]) -> None:
    source = (
        "class P(Object):\n"
        "    def __repr__(self):\n"
        '        return "<P>"\n'
        "P().repr().print()\n"
    )
    assert _printed(source, capsys) == "<P>"


def test_a_user_class_can_define_its_truth(capsys: pytest.CaptureFixture[str]) -> None:
    source = (
        "class P(Object):\n"
        "    def __bool__(self):\n"
        "        return False\n"
        "P().not_().print()\n"
    )
    assert _printed(source, capsys) == "True"


def test_a_user_class_can_define_its_hash(capsys: pytest.CaptureFixture[str]) -> None:
    source = (
        "class P(Object):\n"
        "    def __hash__(self):\n"
        "        return 7\n"
        "{P(), P()}.len().print()\n"
    )
    # Two instances hashing alike still differ by identity, as in Python.
    assert _printed(source, capsys) == "2"


def test_a_declared_length_answers_the_len_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The quiet member of the family: the slot raised nothing and answered
    # nothing, because `len` is how POOP asks and nothing supplied it.
    source = (
        "class P(Object):\n"
        "    def __len__(self):\n"
        "        return 2\n"
        "P().len().print()\n"
    )
    assert _printed(source, capsys) == "2"


def test_a_class_that_defines_len_itself_keeps_it(
    capsys: pytest.CaptureFixture[str],
) -> None:
    source = (
        "class P(Object):\n"
        "    def __len__(self):\n"
        "        return 2\n"
        "    def len(self):\n"
        "        return 99\n"
        "P().len().print()\n"
    )
    assert _printed(source, capsys) == "99"


def test_a_wrong_answer_is_refused_by_role_not_by_slot() -> None:
    # A message spelling `__str__` would name the construct
    # `no_dunder_attribute` bans — and CPython's sentence called `str` the
    # thing that is not a `str`.
    with pytest.raises(ExecutionError, match=r"P's text must be a str, got an int"):
        _run(
            "class P(Object):\n    def __str__(self):\n        return 5\nP().print()\n"
        )


def test_each_slot_names_what_it_wanted() -> None:
    with pytest.raises(ExecutionError, match=r"P's truth must be a bool, got a str"):
        _run(
            "class P(Object):\n"
            "    def __bool__(self):\n"
            '        return "yes"\n'
            "P().not_()\n"
        )
    with pytest.raises(ExecutionError, match=r"P's hash must be an int, got a str"):
        _run('class P(Object):\n    def __hash__(self):\n        return "h"\n{P()}\n')


# --- the ladder has no rung that is not there ---
#
# An alias's one base is the wrapper it stands for, and both are cloaked under
# the builtin's name, so `int.superclass()` answered a class calling itself
# `int` — which `is_identical(int)` then denied.


def test_a_bare_builtin_name_climbs_straight_to_object() -> None:
    from poop.transformers.int import IntTransformer

    alias = IntTransformer.BINDINGS["_poop_int_cls"]
    assert alias.superclass().name() == Str("object")  # ty: ignore[unresolved-attribute]


def test_the_wrapper_and_its_alias_climb_alike() -> None:
    from poop.transformers.list import ListTransformer

    alias = ListTransformer.BINDINGS["_poop_list_cls"]
    assert alias.superclass() == List.superclass()  # ty: ignore[unresolved-attribute]


def test_a_subclass_of_a_builtin_still_sees_the_builtin() -> None:
    # The rung that *is* there: a program's own class descends from the name
    # it wrote, and `list` is what that name answers to.
    ns: dict[str, Any] = dict(DEFAULT_NAMESPACE)
    tree = Interpreter().transform_source(
        "class Stack(list):\n    pass\n"
        "parent = Stack.superclass().name()\n"
        "grandparent = Stack.superclass().superclass().name()\n"
    )
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert ns["parent"] == Str("list")
    assert ns["grandparent"] == Str("object")


def test_the_root_still_answers_none() -> None:
    assert Object.superclass() is none
