from typing import cast

from poop.interpreter import Interpreter
from poop.types.block import Block
from poop.types.boolean import Boolean, false, true
from poop.types.difflib import Difflib, SequenceMatcher
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- SequenceMatcher ---


def test_sequence_matcher_ratio_identical() -> None:
    sm = SequenceMatcher(Str("abc"), Str("abc"))
    assert sm.ratio() == Float(1.0)


def test_sequence_matcher_ratio_disjoint() -> None:
    sm = SequenceMatcher(Str("abc"), Str("xyz"))
    assert sm.ratio() == Float(0.0)


def test_sequence_matcher_ratio_partial() -> None:
    sm = SequenceMatcher(Str("abcd"), Str("abef"))
    result = sm.ratio()
    assert isinstance(result, Float)
    assert 0.0 < result._value < 1.0


def test_sequence_matcher_quick_ratio() -> None:
    sm = SequenceMatcher(Str("abc"), Str("abd"))
    assert isinstance(sm.quick_ratio(), Float)


def test_sequence_matcher_real_quick_ratio() -> None:
    sm = SequenceMatcher(Str("abc"), Str("abc"))
    assert isinstance(sm.real_quick_ratio(), Float)


def test_sequence_matcher_get_matching_blocks() -> None:
    sm = SequenceMatcher(Str("abxcd"), Str("abcd"))
    blocks = sm.get_matching_blocks()
    assert isinstance(blocks, List)
    for entry in blocks:
        assert isinstance(entry, Tuple)
        # Each element of the triple should be an Int.
        for item in entry:
            assert isinstance(item, Int)


def test_sequence_matcher_get_opcodes() -> None:
    sm = SequenceMatcher(Str("abxcd"), Str("abcd"))
    opcodes = sm.get_opcodes()
    assert isinstance(opcodes, List)
    first = opcodes.at(Int(0))
    assert isinstance(first, Tuple)
    tag = first.at(Int(0))
    assert isinstance(tag, Str)


def test_sequence_matcher_find_longest_match() -> None:
    sm = SequenceMatcher(Str("abcdefg"), Str("zzabcdezz"))
    m = sm.find_longest_match()
    assert isinstance(m, Tuple)
    assert m.len() == Int(3)


def test_sequence_matcher_accepts_list_of_str() -> None:
    a = List(Str("line one\n"), Str("line two\n"))
    b = List(Str("line one\n"), Str("line two changed\n"))
    sm = SequenceMatcher(a, b)
    assert 0.0 < sm.ratio()._value < 1.0


# --- Diff producers ---


def test_unified_diff_emits_lines() -> None:
    a = List(Str("alpha\n"), Str("beta\n"))
    b = List(Str("alpha\n"), Str("beta changed\n"))
    diff = Difflib.unified_diff(a, b, fromfile=Str("a"), tofile=Str("b"))
    assert isinstance(diff, List)
    # The diff should contain at least one removed-marker and one added-marker.
    text = "\n".join(cast(Str, line)._value for line in diff)
    assert "-beta" in text
    assert "+beta changed" in text


def test_unified_diff_identical_inputs_empty() -> None:
    a = List(Str("same\n"))
    diff = Difflib.unified_diff(a, a)
    assert isinstance(diff, List)
    assert diff.len() == Int(0)


def test_context_diff_emits_lines() -> None:
    a = List(Str("one\n"))
    b = List(Str("two\n"))
    diff = Difflib.context_diff(a, b)
    assert isinstance(diff, List)
    assert diff.len()._value > 0


def test_ndiff_returns_marked_lines() -> None:
    a = List(Str("alpha\n"))
    b = List(Str("alpha modified\n"))
    diff = Difflib.ndiff(a, b)
    assert isinstance(diff, List)
    text = "\n".join(cast(Str, line)._value for line in diff)
    assert "- " in text
    assert "+ " in text


def test_restore_round_trips_through_ndiff() -> None:
    a = List(Str("hello\n"), Str("world\n"))
    b = List(Str("hello\n"), Str("there\n"))
    diff = Difflib.ndiff(a, b)
    restored = Difflib.restore(diff, Int(1))
    assert isinstance(restored, List)
    assert restored == a


def test_get_close_matches_returns_str_list() -> None:
    word = Str("appel")
    candidates = List(Str("ape"), Str("apple"), Str("peach"), Str("puppy"))
    matches = Difflib.get_close_matches(word, candidates)
    assert isinstance(matches, List)
    assert matches.includes(Str("apple"))


def test_get_close_matches_respects_n() -> None:
    word = Str("hello")
    candidates = List(Str("hallo"), Str("helo"), Str("hello!"), Str("yellow"))
    matches = Difflib.get_close_matches(word, candidates, n=Int(2))
    assert matches.len()._value <= 2


def test_get_close_matches_respects_cutoff() -> None:
    word = Str("alpha")
    candidates = List(Str("zzzz"))
    matches = Difflib.get_close_matches(word, candidates, cutoff=Float(0.9))
    assert matches.len() == Int(0)


# --- Interpreter integration ---


def test_difflib_unified_diff_reachable_via_interpreter() -> None:
    Interpreter().run_source('difflib.unified_diff(["a\\n"], ["b\\n"]).len().print()')


def test_SequenceMatcher_reachable_via_interpreter() -> None:
    Interpreter().run_source('SequenceMatcher("abc", "abd").ratio().print()')


def test_sequence_matcher_isjunk_block_filters_chars() -> None:
    seen: list[Str] = []

    def is_space(c: Str) -> Boolean:
        seen.append(c)
        return true if c == Str(" ") else false

    a, b = Str("ab cd"), Str("ab cd")
    sm = SequenceMatcher(a, b, isjunk=Block(is_space))
    # Identical strings still match perfectly even with the junk hook,
    # and the predicate runs over the inputs.
    assert sm.ratio() == Float(1.0)
    assert any(c == Str(" ") for c in seen)


def test_difflib_get_close_matches_reachable_via_interpreter() -> None:
    Interpreter().run_source(
        'difflib.get_close_matches("appel", ["apple", "peach"]).len().print()'
    )
