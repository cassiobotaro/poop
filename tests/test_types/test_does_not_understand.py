import copy

import pytest

from poop.types._selectors import SMALLTALK_SELECTORS, explain
from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.object import MessageNotUnderstood, Object
from poop.types.string import Str


def test_unknown_message_speaks_smalltalk_not_python() -> None:
    # `'int' object has no attribute` says attribute, not message, in a
    # language whose thesis is that everything is a message.
    with pytest.raises(MessageNotUnderstood) as exc_info:
        Int(5).frobnicate()  # ty: ignore[unresolved-attribute]
    assert "does not understand #frobnicate" in str(exc_info.value)


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
