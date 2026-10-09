import copy
import re

import pytest

from poop.types._selectors import CROSS_LANGUAGE_HINTS, SMALLTALK_SELECTORS, explain
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.object import MessageNotUnderstood, Object
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_unknown_message_speaks_smalltalk_not_python() -> None:
    # `'int' object has no attribute` says attribute, not message, in a
    # language whose thesis is that everything is a message.
    with pytest.raises(
        MessageNotUnderstood, match=re.escape("does not understand #frobnicate")
    ):
        Int(5).frobnicate()  # ty: ignore[unresolved-attribute]


def test_unknown_message_points_at_methods_when_it_has_no_hint() -> None:
    with pytest.raises(MessageNotUnderstood, match=":methods"):
        Int(5).frobnicate()  # ty: ignore[unresolved-attribute]


def test_unknown_message_suggests_a_close_match() -> None:
    assert "did you mean #upper?" in explain(Str("x"), "uppercase")


def test_unknown_message_does_not_invent_a_match_for_a_meaningless_name() -> None:
    # difflib's default cutoff answers `from_bytes` here, which is worse than
    # silence: it names a message the user never meant.
    assert "did you mean" not in explain(Int(5), "frobnicate")
    assert "did you mean" not in explain(List(Int(1)), "blerg")


def test_smalltalk_selector_maps_to_the_poop_message() -> None:
    # difflib cannot reach this one — `size` and `len` share no letters.
    assert "Smalltalk's #size is #len here" in explain(List(Int(1)), "size")


def test_smalltalk_selector_table_only_maps_to_messages_that_exist() -> None:
    # A table pointing at a message POOP does not have would be worse than no
    # table: it would teach a name that fails on the next line.
    probes: list[object] = [List(Int(1)), Int(1), Str("a"), true, none]
    for selector, poop_name in SMALLTALK_SELECTORS.items():
        assert any(hasattr(p, poop_name) for p in probes), (
            f"#{selector} maps to #{poop_name}, which no POOP type answers"
        )


def test_smalltalk_selector_is_ignored_when_the_receiver_lacks_the_target() -> None:
    # `size` maps to `len`, but Int has no len — do not promise one.
    assert "Smalltalk" not in explain(Int(5), "size")


# the cross-language hints (Python 3.15's `_CROSS_LANGUAGE_HINTS`)


@pytest.mark.parametrize(
    ("receiver", "name", "hint"),
    [
        (List(Int(1)), "push", "did you mean #append?"),
        (Str("a"), "toUpperCase", "did you mean #upper?"),
        (Dict(), "keySet", "did you mean #keys?"),
        # CPython says `Use d[k] = v.` and `Use 'x in list'.`; both name a
        # construct POOP forbids, so the row names the message instead.
        (Dict(), "put", "did you mean #at_put?"),
        (List(Int(1)), "contains", "did you mean #includes?"),
        # A mutable message on an immutable receiver.
        (Tuple(Int(1)), "append", "did you mean to use a list?"),
        (FrozenSet(Int(1)), "add", "did you mean to use a set?"),
    ],
    ids=[
        "push",
        "toUpperCase",
        "keySet",
        "put",
        "contains",
        "tuple_append",
        "frozenset_add",
    ],
)
def test_a_name_from_another_language_names_the_poop_message(
    receiver: object, name: str, hint: str
) -> None:
    assert explain(receiver, name) == (
        f"{type(receiver).__name__} does not understand #{name} — {hint}"
    )


def test_the_foreign_rows_are_keyed_by_receiver() -> None:
    # `push` is a list word; a str has no row for it and falls through to
    # the ordinary hint.
    assert "append" not in explain(Str("a"), "push")


def test_the_foreign_rows_reach_a_subclass() -> None:
    # CPython matches with `isinstance`, so `class Stack(list)` gets the
    # list rows; POOP walks the MRO for the same result.
    class Stack(List):
        __slots__ = ()

    assert "did you mean #append?" in explain(Stack(), "push")


def test_every_foreign_row_names_a_message_the_receiver_answers() -> None:
    # A row pointing at a message the receiver lacks would teach a name that
    # fails on the next line — the same rule the Smalltalk table is held to.
    samples: dict[str, object] = {
        "list": List(),
        "str": Str(""),
        "dict": Dict(),
        "tuple": Tuple(),
        "frozenset": FrozenSet(),
    }
    for (kind, _), hint in CROSS_LANGUAGE_HINTS.items():
        match = re.search(r"#(\w+)\?", hint)
        if match is not None:
            assert hasattr(samples[kind], match.group(1)), (
                f"{kind} lacks #{match.group(1)}"
            )


# the nested-attribute hint (Python 3.15)


class _Square(Object):
    __slots__ = ("side",)

    def __init__(self) -> None:
        self.side = Int(2)

    def area(self) -> Object:
        return self.side * self.side


class _Tile(Object):
    __slots__ = ("inner",)

    def __init__(self) -> None:
        self.inner = _Square()


def test_a_message_the_inner_object_answers_is_suggested_one_level_deep() -> None:
    assert explain(_Tile(), "area").endswith("did you mean #inner.area?")


def test_the_nested_hint_runs_nothing() -> None:
    # A property is a descriptor; reading it to look inside would run code
    # while composing a refusal. CPython skips descriptors for the same reason.
    class _Trap(Object):
        __slots__ = ()

        @property
        def inner(self) -> object:
            raise AssertionError("the hint read a property")

    assert "inner" not in explain(_Trap(), "area")


def test_message_not_understood_is_an_attribute_error() -> None:
    # hasattr and three-argument getattr swallow AttributeError and nothing
    # else; a plainer base would turn Object.has_attr into a crash.
    assert issubclass(MessageNotUnderstood, AttributeError)


def test_hasattr_still_answers_false_for_an_unknown_message() -> None:
    assert hasattr(Int(5), "frobnicate") is False
    assert Int(5).has_attr(Str("frobnicate")) is false


def test_get_attr_with_default_still_answers_the_default() -> None:
    assert Int(5).get_attr(Str("frobnicate"), "fallback") == "fallback"


def test_known_message_never_reaches_the_hook() -> None:
    assert Int(5).abs() == Int(5)
    assert Str("x").upper() == Str("X")


def test_dunder_probes_never_reach_the_hook() -> None:
    # Python probes __copy__/__getstate__ on any object; routing those to the
    # hook is the classic proxy bug.
    class _Spy(Object):
        __slots__ = ()

        def does_not_understand(self, name: str) -> object:
            raise AssertionError(f"the hook saw dunder {name!r}")

    copy.copy(_Spy())


def test_does_not_understand_is_the_hook_a_proxy_overrides() -> None:
    # Answering a callable is also the only way to reach the arguments:
    # attribute lookup runs before the call.
    class _Logging(Object):
        __slots__ = ("_log", "_target")

        def __init__(self, target: object, log: list[str]) -> None:
            self._target = target
            self._log = log

        def does_not_understand(self, name: str) -> object:
            def forward(*args: object) -> object:
                self._log.append(name)
                return getattr(self._target, name)(*args)

            return forward

    log: list[str] = []
    proxy = _Logging(Str("hello"), log)
    assert proxy.upper() == Str("HELLO")  # ty: ignore[unresolved-attribute]
    assert log == ["upper"]
