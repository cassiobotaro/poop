"""Which class a message's wrong-arity sentence names.

The sentence stays CPython's; the class inside it is the one CPython would
name, the class that defines the message, as a program can write it.
"""

from types import MethodType

import pytest

from poop.errors import ExecutionError
from poop.interpreter import Interpreter
from poop.types.block import _MethodBlock
from poop.types.int import Int
from poop.types.list import List
from poop.types.meta import PoopMeta


def _refusal(source: str) -> str:
    with pytest.raises(ExecutionError) as info:
        Interpreter().run_source(source + "\n")
    return info.value.message


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "[1].map(lambda x: x, 2)",
            "list.map() takes from 1 to 2 positional arguments but 3 were given",
        ),
        (
            "[1].iter().has_next(1)",
            "list_iterator.has_next() takes 1 positional argument but 2 were given",
        ),
        (
            '{"a": 1}.keys().mapping(1)',
            "dict_keys.mapping() takes 1 positional argument but 2 were given",
        ),
    ],
    ids=["map", "has_next", "mapping"],
)
def test_a_mixin_message_names_the_receivers_builtin(
    source: str, expected: str
) -> None:
    assert _refusal(source) == f"TypeError: {expected}"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "(5).repr(1)",
            "object.repr() takes 1 positional argument but 2 were given",
        ),
        (
            "class Stack(list):\n    pass\nStack().append()",
            "list.append() missing 1 required positional argument: 'obj'",
        ),
        (
            "Try(lambda: 1).except_(ValueError)",
            "Try.except_() missing 1 required positional argument: 'handler'",
        ),
    ],
    ids=["object-defines-it", "subclass-of-list", "a-poop-construct"],
)
def test_the_class_cpython_would_name_is_kept(source: str, expected: str) -> None:
    assert _refusal(source) == f"TypeError: {expected}"


def test_an_unexpected_keyword_is_renamed_too() -> None:
    assert _refusal("[1].map(lambda x: x, nope=1)") == (
        "TypeError: list.map() got an unexpected keyword argument 'nope'"
    )


def test_a_type_error_the_body_raises_passes_through_untouched(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Installed on the mixin `map` comes from, so the rename *would* apply to
    # a binding failure; this one is raised inside the body, below `__call__`.
    mixin = next(
        cls
        for cls in List.__mro__
        if "map" in vars(cls) and not isinstance(cls, PoopMeta)
    )

    def boom(self: object) -> None:
        raise TypeError("object.boom() is a sentence the body wrote")

    boom.__qualname__ = "object.boom"
    monkeypatch.setattr(mixin, "boom", boom, raising=False)
    with pytest.raises(TypeError) as info:
        _MethodBlock(MethodType(boom, List(Int(1))))()
    assert str(info.value) == "object.boom() is a sentence the body wrote"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            'bytearray(b"a").lower(1)',
            "bytearray.lower() takes 1 positional argument but 2 were given",
        ),
        (
            'frozendict({"a": 1}).keys(1)',
            "frozendict.keys() takes 1 positional argument but 2 were given",
        ),
    ],
    ids=["bytearray", "frozendict"],
)
def test_bytearray_and_frozendict_name_themselves(source: str, expected: str) -> None:
    # Both reuse another wrapper's functions (`bytes`, `dict`); CPython's two
    # types define their own, and `frozendict` is not a `dict` there.
    assert _refusal(source) == f"TypeError: {expected}"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("int.hash(1)", "int.hash() takes 1 positional argument but 2 were given"),
        (
            "class Foo(Object):\n    pass\nFoo.repr(1)",
            "Foo.repr() takes 1 positional argument but 2 were given",
        ),
    ],
    ids=["builtin", "program-class"],
)
def test_a_class_side_message_names_the_class(source: str, expected: str) -> None:
    # One class-side function is shared by every class, and was cloaked to the
    # bare message name: `hash() takes …`. CPython's `int.mro(1)` names `int`.
    assert _refusal(source) == f"TypeError: {expected}"


@pytest.mark.parametrize(
    "source", ['bytearray(b"ab").maketrans(b"a")', 'bytearray.maketrans(b"a")']
)
def test_a_staticmethod_names_the_class_it_was_read_through(source: str) -> None:
    # No receiver to read: the `message` descriptor hands over the class.
    # `Bytes` defines `maketrans`, and this used to blame `bytes.maketrans()`.
    assert _refusal(source) == (
        "TypeError: bytearray.maketrans() missing 1 required positional argument: 'to'"
    )


def test_a_binding_failure_without_the_callees_name_passes_through() -> None:
    # CPython's own classmethod reports without its class (`from_bytes()`, not
    # `int.from_bytes()`), so there is no frozen prefix to rename.
    with pytest.raises(TypeError) as info:
        _MethodBlock(int.from_bytes)()  # ty: ignore[missing-argument]
    assert str(info.value).startswith("from_bytes() missing required argument")


def test_a_function_with_no_receiver_and_no_class_keeps_its_name() -> None:
    # A `_MethodBlock` over a bare function, built without the class a
    # `staticmethod` is read through: its own qualname is all there is.
    def lone() -> None:
        pass

    lone.__qualname__ = "str.lone"
    lone.__name__ = "lone"
    with pytest.raises(TypeError) as info:
        _MethodBlock(lone)(1)  # ty: ignore[too-many-positional-arguments]
    assert str(info.value) == "str.lone() takes 0 positional arguments but 1 was given"


@pytest.mark.parametrize(
    ("handler", "expected"),
    [
        (
            "e.message(1)",
            "ValueError.message() takes 1 positional argument but 2 were given",
        ),
        ("e.repr(1)", "object.repr() takes 1 positional argument but 2 were given"),
    ],
    ids=["its-own-message", "a-message-object-defines"],
)
def test_a_caught_error_names_its_exceptions_class(handler: str, expected: str) -> None:
    # `Error` is cloaked as `object`, and `e.message(1)` blamed `object.message()`
    # for an error whose `class_name()` is `ValueError`.
    source = (
        'Try(lambda: ValueError.raise_("x"))'
        f".except_(ValueError, lambda e: {handler}).run()"
    )
    assert _refusal(source) == f"TypeError: {expected}"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "True.if_true()",
            "#if_true expects a block, got nothing — write .if_true(lambda: …)",
        ),
        ("True.and_()", "#and_ expects a block, got nothing — write .and_(lambda: …)"),
        (
            "None.if_none()",
            "#if_none expects a block, got nothing — write .if_none(lambda: …)",
        ),
        (
            "(5).if_none_if_not_none()",
            "#if_none_if_not_none expects a block, got nothing — "
            "write .if_none_if_not_none(lambda: …, lambda x: …)",
        ),
        (
            "(lambda: True).while_true()",
            "#while_true expects a block, got nothing — write .while_true(lambda: …)",
        ),
    ],
    ids=["a-boolean", "and_", "none", "an-object", "a-block"],
)
def test_a_missing_block_in_the_branch_family_is_refused_with_the_hint(
    source: str, expected: str
) -> None:
    # The substitutes for `if`, `and`/`or` and `while` answered CPython's
    # `bool.if_true() missing 1 required positional argument: 'block'`, while
    # `[1].map()` already answered the hint. They take `MISSING` defaults now.
    assert _refusal(source) == f"TypeError: {expected}"


def test_a_missing_second_block_runs_neither() -> None:
    # Both slots are checked before either block runs.
    assert _refusal('True.if_true_if_false(lambda: "ran".print())').startswith(
        "TypeError: #if_true_if_false expects a block, got nothing"
    )


@pytest.mark.parametrize(
    ("source", "selector"),
    [
        ("True.if_false_if_true(5, 5)", "if_false_if_true"),
        ("True.if_true_if_false(lambda: 1)", "if_true_if_false"),
    ],
    ids=["non-block", "missing"],
)
def test_a_boolean_pair_hints_both_blocks(source: str, selector: str) -> None:
    # It showed one (`.if_true_if_false(lambda: …)`) for a message taking two,
    # where the null pairs already show both.
    assert _refusal(source).endswith(f"— write .{selector}(lambda: …, lambda: …)")
