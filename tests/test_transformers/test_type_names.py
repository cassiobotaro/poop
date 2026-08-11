"""Tests that POOP type bindings are mangled, not publicly visible.

Lowercase Python builtins (`int`, `list`, ...) are rewritten at parse time
to the mangled `_poop_*` name so `x.is_instance(int)` works. The mangled
names live in the namespace; the PascalCase ones do not, keeping the
user-facing globals limited to true entry points (`Try`, `Path`, `With`).
"""

import pytest

from poop import Interpreter
from poop.transformers import DEFAULT_NAMESPACE
from poop.types._alias import unalias
from poop.types.block import Block
from poop.types.boolean import Boolean
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.complex import Complex
from poop.types.dict import Dict
from poop.types.enumerate import Enumerate
from poop.types.float import Float
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.memory_view import MemoryView
from poop.types.object import Object
from poop.types.range import Range
from poop.types.set import Set
from poop.types.slice import Slice
from poop.types.string import Str
from poop.types.tuple import Tuple
from poop.types.zip import Zip


def _eval(source: str) -> object:
    interpreter = Interpreter()
    tree = interpreter.transform_source(f"result = {source}")
    ns = dict(DEFAULT_NAMESPACE)
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    return ns["result"]


@pytest.mark.parametrize(
    ("mangled", "type_"),
    [
        ("_poop_bool_cls", Boolean),
        ("_poop_str_cls", Str),
        ("_poop_int_cls", Int),
        ("_poop_float_cls", Float),
        ("_poop_list_cls", List),
        ("_poop_tuple_cls", Tuple),
        ("_poop_dict_cls", Dict),
        ("_poop_set_cls", Set),
        ("_poop_frozenset_cls", FrozenSet),
        ("_poop_bytes_cls", Bytes),
        ("_poop_bytearray_cls", ByteArray),
        ("_poop_memoryview_cls", MemoryView),
        ("_poop_complex_cls", Complex),
        ("_poop_range_cls", Range),
        ("_poop_enumerate_cls", Enumerate),
        ("_poop_zip_cls", Zip),
        ("_poop_block", Block),
        ("_poop_object", Object),
        ("_poop_slice", Slice),
    ],
)
def test_mangled_type_binding_is_in_default_namespace(
    mangled: str, type_: type
) -> None:
    # `_cls` bindings are the alias a bare name resolves to — a subclass of the
    # wrapper whose *call* is the converter, so that `x = list; x([1, 2])`
    # answers what `list([1, 2])` answers. `unalias` is the question this test
    # has always been asking: which POOP type does the name stand for.
    assert unalias(DEFAULT_NAMESPACE[mangled]) is type_


@pytest.mark.parametrize(
    ("lowercase", "argument", "expected"),
    [
        ("list", "[1, 2]", "[1, 2]"),
        ("tuple", "[1, 2]", "(1, 2)"),
        ("set", "[1, 2]", "{1, 2}"),
        ("frozenset", "[1, 2]", "frozenset({1, 2})"),
        ("int", "(4.9)", "4"),
        ("float", "(2)", "2.0"),
        ("str", "(5)", "5"),
        ("complex", "(1)", "(1+0j)"),
        ("bytes", "[65]", "b'A'"),
        ("bytearray", "[65]", "bytearray(b'A')"),
        ("range", "(3)", "range(0, 3)"),
        ("dict", "", "{}"),
    ],
)
def test_an_aliased_constructor_answers_what_the_direct_call_answers(
    lowercase: str, argument: str, expected: str
) -> None:
    """A constructor is an object, so it travels — and had to stop meaning
    something else once it did. `x = list; x([1, 2])` answered `[[1, 2]]`,
    because a bare name resolved to the class (variadic, "build from these
    elements") while the call resolved to the converter.
    """
    direct = _eval(f"{lowercase}({argument})")
    aliased = _eval(f"(lambda c: c({argument}))({lowercase})")
    assert str(direct) == expected
    assert str(aliased) == expected


@pytest.mark.parametrize(
    ("lowercase", "argument", "expected"),
    [
        ("list", "[1, 2]", "[1, 2]"),
        ("tuple", "[1, 2]", "(1, 2)"),
        ("set", "[1, 2]", "{1, 2}"),
        ("frozenset", "[1, 2]", "frozenset({1, 2})"),
        ("int", "(4.9)", "4"),
        ("float", "(2)", "2.0"),
        ("str", "(5)", "5"),
        ("complex", "(1)", "(1+0j)"),
        ("bytes", "[65]", "b'A'"),
        ("bytearray", "[65]", "bytearray(b'A')"),
        ("range", "(3)", "range(0, 3)"),
        ("dict", "", "{}"),
    ],
)
def test_a_subclass_constructs_the_way_its_builtin_does(
    lowercase: str, argument: str, expected: str
) -> None:
    """The same gap, one level down — and `class Stack(list)` is sanctioned.

    Every row disagreed with the direct call: seven silently (`Stack([1, 2])`
    held one list, `N(4.9)` an int holding 4.9) and six by refusing in
    Python's words. `bool` is not here: its two values are singletons with no
    payload to rebuild, so its converter's answer passes through.
    """
    ns = dict(DEFAULT_NAMESPACE)
    tree = Interpreter().transform_source(
        f"class Sub({lowercase}):\n    pass\n"
        f"made = Sub({argument})\n"
        "kind = made.class_name()\n"
    )
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert str(ns["made"]) == expected
    assert str(ns["kind"]) == "Sub"


def test_a_subclass_with_its_own_init_still_uses_it() -> None:
    # What reading `_converter` off `cls.__dict__` was protecting.
    ns = dict(DEFAULT_NAMESPACE)
    tree = Interpreter().transform_source(
        "class Pair(list):\n"
        "    def __init__(self, a, b):\n"
        "        self.first = a\n"
        "made = Pair(1, 2)\n"
        "first = made.first\n"
        "kind = made.class_name()\n"
    )
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert str(ns["first"]) == "1"
    assert str(ns["kind"]) == "Pair"


def test_a_subclass_does_not_share_the_payload_it_was_built_from() -> None:
    # A converter may answer a value it was handed, and two objects sharing
    # one list would be one object wearing two classes.
    ns = dict(DEFAULT_NAMESPACE)
    tree = Interpreter().transform_source(
        "class Stack(list):\n    pass\n"
        "source = [1, 2]\n"
        "made = Stack(source)\n"
        "made.append(3)\n"
    )
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert str(ns["source"]) == "[1, 2]"
    assert str(ns["made"]) == "[1, 2, 3]"


def test_bool_cannot_be_subclassed() -> None:
    """`Boolean` has no payload: its two values are the whole class.

    CPython refuses it as a base outright (`type 'bool' is not an acceptable
    base type`). POOP let the class be defined and failed at the first
    instance with `Can't instantiate abstract class Flag without an
    implementation for abstract methods '__bool__', '__str__', …` — a dozen
    dunders in one sentence, from a program that spelled none.
    """
    ns = dict(DEFAULT_NAMESPACE)
    tree = Interpreter().transform_source("class Flag(bool):\n    pass\n")
    with pytest.raises(TypeError, match="^bool cannot be subclassed — "):
        exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102


def test_an_alias_still_serves_as_a_type_argument_and_a_base() -> None:
    # The three things a bare builtin name is otherwise used for.
    assert bool(_eval("[1].is_instance(list)")) is True
    assert bool(_eval("[1].is_instance(tuple)")) is False
    assert str(_eval("list.name()")) == "list"

    interpreter = Interpreter()
    ns = dict(DEFAULT_NAMESPACE)
    tree = interpreter.transform_source(
        "class Stack(list):\n    pass\n"
        "s = Stack()\n"
        "s.append(1)\n"
        "kind = s.class_name()\n"
        "same = s.is_instance(list)\n"
        "narrow = [1].is_instance(Stack)\n"
    )
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert str(ns["s"]) == "[1]"
    assert str(ns["kind"]) == "Stack"
    assert bool(ns["same"]) is True
    # `_wrapped` is read off `__dict__`, not inherited, or a subclass of the
    # alias would match every instance of the wrapper.
    assert bool(ns["narrow"]) is False


@pytest.mark.parametrize(
    "pascal",
    [
        "Boolean",
        "Str",
        "Int",
        "Float",
        "List",
        "Tuple",
        "Dict",
        "Set",
        "FrozenSet",
        "Bytes",
        "ByteArray",
        "MemoryView",
        "Complex",
        "Range",
        "Enumerate",
        "Zip",
        "Block",
        "Object",
        "Slice",
        "Map",
        "Filter",
    ],
)
def test_pascal_type_name_is_not_in_default_namespace(pascal: str) -> None:
    assert pascal not in DEFAULT_NAMESPACE


@pytest.mark.parametrize(
    ("literal", "lowercase"),
    [
        ('"hi"', "str"),
        ("(42)", "int"),
        ("(3.14)", "float"),
        ("True", "bool"),
        ("[1]", "list"),
        ("(1,)", "tuple"),
        ("{1: 2}", "dict"),
        ("{1, 2}", "set"),
    ],
)
def test_is_instance_lowercase_name_resolves_to_poop_type(
    literal: str, lowercase: str
) -> None:
    assert bool(_eval(f"{literal}.is_instance({lowercase})")) is True


@pytest.mark.parametrize(
    ("type_", "lowercase"),
    [
        (Boolean, "bool"),
        (Str, "str"),
        (Int, "int"),
        (Float, "float"),
        (List, "list"),
        (Tuple, "tuple"),
        (Dict, "dict"),
        (Set, "set"),
        (FrozenSet, "frozenset"),
        (Bytes, "bytes"),
        (ByteArray, "bytearray"),
        (MemoryView, "memoryview"),
        (Complex, "complex"),
        (Range, "range"),
        (Enumerate, "enumerate"),
        (Zip, "zip"),
        (Object, "object"),
    ],
)
def test_type_repr_mimics_python_builtin(type_: type, lowercase: str) -> None:
    assert repr(type_) == f"<class '{lowercase}'>"


@pytest.mark.parametrize(
    ("type_", "lowercase"),
    [
        (Str, "str"),
        (Int, "int"),
        (Float, "float"),
        (List, "list"),
        (Tuple, "tuple"),
        (Dict, "dict"),
        (Set, "set"),
        (FrozenSet, "frozenset"),
        (Bytes, "bytes"),
        (ByteArray, "bytearray"),
        (MemoryView, "memoryview"),
        (Complex, "complex"),
        (Range, "range"),
        (Enumerate, "enumerate"),
        (Zip, "zip"),
        (Object, "object"),
    ],
)
def test_class_name_returns_lowercase_for_poop_builtins(
    type_: type, lowercase: str
) -> None:
    assert type_.__name__ == lowercase


# --- the one dunder call POOP sanctions ---
#
# `no_dunder_attribute` carves out `__init__` *for* `super().__init__(...)`,
# so it is the constructor a program is invited to write — and it reached the
# wrapper's variadic `__init__`, which means "build from these elements".


@pytest.mark.parametrize(
    ("lowercase", "argument", "expected"),
    [
        ("list", "[1, 2]", "[1, 2]"),
        ("tuple", "[1, 2]", "(1, 2)"),
        ("set", "[1, 2]", "{1, 2}"),
        ("int", "(4.9)", "4"),
        ("str", "(5)", "5"),
        ("dict", '({"a": 1})', "{'a': 1}"),
        ("bytes", "[65]", "b'A'"),
    ],
)
def test_super_init_converts_like_the_builtin_call(
    lowercase: str, argument: str, expected: str
) -> None:
    ns = dict(DEFAULT_NAMESPACE)
    tree = Interpreter().transform_source(
        f"class Sub({lowercase}):\n"
        "    def __init__(self, value):\n"
        "        super().__init__(value)\n"
        f"made = Sub({argument})\n"
        "kind = made.class_name()\n"
    )
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert str(ns["made"]) == expected
    assert str(ns["kind"]) == "Sub"


def test_super_init_leaves_room_for_the_subclass_own_state() -> None:
    ns = dict(DEFAULT_NAMESPACE)
    tree = Interpreter().transform_source(
        "class Tagged(list):\n"
        "    def __init__(self, xs, tag):\n"
        "        super().__init__(xs)\n"
        "        self.tag = tag\n"
        "made = Tagged([1, 2], 'x')\n"
        "tag = made.tag\n"
    )
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert str(ns["made"]) == "[1, 2]"
    assert str(ns["tag"]) == "x"


def test_super_init_refuses_over_supply_the_way_the_call_does() -> None:
    # `super().__init__(*xs)` was the spelling that worked while the plain one
    # was broken; it now answers what `list(1, 2)` answers, which is what
    # CPython answers to `list.__init__(self, 1, 2)`.
    ns = dict(DEFAULT_NAMESPACE)
    tree = Interpreter().transform_source(
        "class Sub(list):\n"
        "    def __init__(self, xs):\n"
        "        super().__init__(*xs)\n"
        "made = Sub([1, 2])\n"
    )
    with pytest.raises(TypeError, match="list is built from at most one collection"):
        exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102


# --- the `__new__` step Python has and POOP did not ---
#
# For an immutable builtin CPython sets the value in `__new__`, from the
# constructor's arguments, before `__init__` is reached — so a subclass whose
# `__init__` ignores them still comes back working. POOP writes the payload in
# `__init__`, so one that never passed it up left the object with none.


@pytest.mark.parametrize(
    ("lowercase", "argument", "expected"),
    [
        ("int", "(4.9)", "4"),
        ("float", "(2)", "2.0"),
        ("str", "(5)", "5"),
        ("complex", "(1)", "(1+0j)"),
        ("bytes", "[65]", "b'A'"),
        ("tuple", "[1, 2]", "(1, 2)"),
        ("frozenset", "[1, 2]", "frozenset({1, 2})"),
        # The mutable four are filled by `__init__` in CPython too, which is
        # why they agreed all along — they are here so the row stays pinned.
        ("list", "[1, 2]", "[1, 2]"),
        ("dict", '({"a": 1})', "{'a': 1}"),
        ("set", "[1, 2]", "{1, 2}"),
        ("bytearray", "[65]", "bytearray(b'A')"),
    ],
)
def test_an_init_that_ignores_its_argument_still_gets_the_value(
    lowercase: str, argument: str, expected: str
) -> None:
    ns = dict(DEFAULT_NAMESPACE)
    tree = Interpreter().transform_source(
        f"class Sub({lowercase}):\n"
        "    def __init__(self, value):\n"
        "        pass\n"
        f"made = Sub({argument})\n"
        "kind = made.class_name()\n"
    )
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert str(ns["made"]) == expected
    assert str(ns["kind"]) == "Sub"


def test_a_subclass_with_its_own_signature_is_left_to_its_init() -> None:
    # Two arguments are not the shape a converter takes, so nothing is
    # pre-filled and `super()` does the work from inside `__init__`.
    ns = dict(DEFAULT_NAMESPACE)
    tree = Interpreter().transform_source(
        "class Tagged(list):\n"
        "    def __init__(self, xs, tag):\n"
        "        super().__init__(xs)\n"
        "        self.tag = tag\n"
        "made = Tagged([1, 2], 'x')\n"
        "tag = made.tag\n"
    )
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert str(ns["made"]) == "[1, 2]"
    assert str(ns["tag"]) == "x"


def test_a_builtin_with_no_empty_cannot_be_built_without_a_value() -> None:
    """A signature of its own *and* no `super()` call.

    CPython refuses this at construction too — `int.__new__` cannot take
    those arguments — and refusing here rather than at the first message
    keeps the report where the mistake is. What POOP may not do either way is
    answer `#_value`, the internal slot name.
    """
    ns = dict(DEFAULT_NAMESPACE)
    tree = Interpreter().transform_source(
        "class N(int):\n    def __init__(self, a, b):\n        pass\nmade = N(1, 2)\n"
    )
    with pytest.raises(TypeError, match="was built without its value"):
        exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102


def test_a_builtin_with_an_empty_starts_from_it() -> None:
    # `list.__new__` hands `__init__` an empty list, so a subclass with a
    # signature of its own is an ordinary empty list carrying its own state —
    # which is what CPython answers here.
    ns = dict(DEFAULT_NAMESPACE)
    tree = Interpreter().transform_source(
        "class Pair(list):\n"
        "    def __init__(self, a, b):\n"
        "        self.first = a\n"
        "made = Pair(1, 2)\n"
        "size = made.len()\n"
        "first = made.first\n"
    )
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    assert str(ns["made"]) == "[]"
    assert str(ns["size"]) == "0"
    assert str(ns["first"]) == "1"
