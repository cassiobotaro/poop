import re as _re

import pytest

from poop.interpreter import Interpreter
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.re import Match, Pattern, Re
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_match_returns_match_on_success() -> None:
    m = Re.match(Str(r"\d+"), Str("123abc"))
    assert isinstance(m, Match)
    assert m.group() == Str("123")


def test_match_returns_none_on_failure() -> None:
    assert Re.match(Str(r"\d+"), Str("abc")) is none


def test_search_finds_match_anywhere() -> None:
    m = Re.search(Str(r"\d+"), Str("abc123def"))
    assert isinstance(m, Match)
    assert m.group() == Str("123")


def test_fullmatch_requires_full_string() -> None:
    assert isinstance(Re.fullmatch(Str(r"\d+"), Str("123")), Match)
    assert Re.fullmatch(Str(r"\d+"), Str("123abc")) is none


def test_findall_returns_list_of_str_no_groups() -> None:
    out = Re.findall(Str(r"\d+"), Str("a1 b22 c333"))
    assert isinstance(out, List)
    assert out.at(Int(0)) == Str("1")
    assert out.at(Int(2)) == Str("333")


def test_findall_with_groups_returns_list_of_tuple() -> None:
    out = Re.findall(Str(r"(\w)=(\d)"), Str("a=1 b=2"))
    first = out.at(Int(0))
    assert isinstance(first, Tuple)
    assert first.at(Int(0)) == Str("a")
    assert first.at(Int(1)) == Str("1")


def test_finditer_returns_tuple_of_match() -> None:
    out = Re.finditer(Str(r"\d+"), Str("a1 b22"))
    assert isinstance(out, Tuple)
    assert out.len() == Int(2)
    first = out.at(Int(0))
    assert isinstance(first, Match)
    assert first.group() == Str("1")


def test_sub_substitutes() -> None:
    out = Re.sub(Str(r"\d+"), Str("X"), Str("a1 b22"))
    assert out == Str("aX bX")


def test_sub_with_count() -> None:
    out = Re.sub(Str(r"\d+"), Str("X"), Str("a1 b22 c333"), Int(2))
    assert out == Str("aX bX c333")


def test_subn_returns_str_count_tuple() -> None:
    out = Re.subn(Str(r"\d+"), Str("X"), Str("a1 b22"))
    assert isinstance(out, Tuple)
    assert out.at(Int(0)) == Str("aX bX")
    assert out.at(Int(1)) == Int(2)


def test_sub_with_callable_replacement() -> None:
    # proposal 123: re.sub accepts a callable (Block) replacement.
    from poop.types.block import Block

    out = Re.sub(Str("a"), Block(lambda m: Str("X")), Str("banana"))
    assert out == Str("bXnXnX")


def test_sub_callable_receives_match() -> None:
    from poop.types.block import Block

    out = Re.sub(
        Str(r"\d+"),
        Block(lambda m: Str(m.group()._value * 2)),
        Str("a1b2"),
    )
    assert out == Str("a11b22")


def test_pattern_sub_with_callable() -> None:
    from poop.types.block import Block

    p = Re.compile(Str("a"))
    assert p.sub(Block(lambda m: Str("Z")), Str("banana")) == Str("bZnZnZ")


def test_sub_callable_via_interpreter() -> None:
    Interpreter().run_source('re.sub("a", lambda m: "X", "banana").print()')


def test_split_returns_list() -> None:
    out = Re.split(Str(r"\s+"), Str("a  b   c"))
    assert isinstance(out, List)
    assert out.at(Int(0)) == Str("a")
    assert out.at(Int(2)) == Str("c")


def test_split_with_maxsplit() -> None:
    out = Re.split(Str(r","), Str("a,b,c,d"), Int(2))
    assert out.len() == Int(3)
    assert out.at(Int(2)) == Str("c,d")


def test_escape_escapes_meta_chars() -> None:
    out = Re.escape(Str("a.b*c"))
    assert out == Str(_re.escape("a.b*c"))


def test_compile_returns_pattern() -> None:
    p = Re.compile(Str(r"\d+"))
    assert isinstance(p, Pattern)


def test_re_flags_are_int() -> None:
    assert Re.IGNORECASE == Int(int(_re.IGNORECASE))
    assert Re.MULTILINE == Int(int(_re.MULTILINE))
    assert Re.DOTALL == Int(int(_re.DOTALL))
    assert Re.VERBOSE == Int(int(_re.VERBOSE))
    assert Re.ASCII == Int(int(_re.ASCII))
    assert Re.UNICODE == Int(int(_re.UNICODE))
    assert Re.LOCALE == Int(int(_re.LOCALE))
    assert Re.DEBUG == Int(int(_re.DEBUG))


def test_re_ignorecase_flag_works() -> None:
    m = Re.search(Str(r"abc"), Str("ABC"), Re.IGNORECASE)
    assert isinstance(m, Match)


def test_re_pattern_match_class_attrs() -> None:
    assert Re.Pattern is Pattern
    assert Re.Match is Match


def test_pattern_match_search_fullmatch() -> None:
    p = Re.compile(Str(r"\d+"))
    assert isinstance(p.match(Str("123")), Match)
    assert isinstance(p.search(Str("abc123")), Match)
    assert isinstance(p.fullmatch(Str("123")), Match)
    assert p.match(Str("abc")) is none


def test_pattern_findall_finditer() -> None:
    p = Re.compile(Str(r"\d+"))
    assert isinstance(p.findall(Str("1 2 3")), List)
    assert isinstance(p.finditer(Str("1 2 3")), Tuple)


def test_pattern_sub_subn_split() -> None:
    p = Re.compile(Str(r"\d"))
    assert p.sub(Str("X"), Str("a1b2")) == Str("aXbX")
    sn = p.subn(Str("X"), Str("a1b2"))
    assert sn.at(Int(0)) == Str("aXbX")
    assert sn.at(Int(1)) == Int(2)
    parts = p.split(Str("a1b2c"))
    assert isinstance(parts, List)


def test_pattern_pattern_property() -> None:
    p = Re.compile(Str(r"\d+"))
    assert p.pattern == Str(r"\d+")


def test_pattern_flags_property() -> None:
    p = Re.compile(Str(r"\d+"), Re.IGNORECASE)
    assert isinstance(p.flags, Int)
    assert p.flags._value & int(_re.IGNORECASE) == int(_re.IGNORECASE)


def test_pattern_groups_property() -> None:
    p = Re.compile(Str(r"(\w+)=(\d+)"))
    assert p.groups == Int(2)


def test_pattern_groupindex_property() -> None:
    p = Re.compile(Str(r"(?P<name>\w+)=(?P<value>\d+)"))
    gi = p.groupindex
    assert isinstance(gi, Dict)
    assert gi.at(Str("name")) == Int(1)
    assert gi.at(Str("value")) == Int(2)


def test_match_group_no_args() -> None:
    m = Re.match(Str(r"(\w+)=(\d+)"), Str("x=42"))
    assert isinstance(m, Match)
    assert m.group() == Str("x=42")


def test_match_group_by_index() -> None:
    m = Re.match(Str(r"(\w+)=(\d+)"), Str("x=42"))
    assert isinstance(m, Match)
    assert m.group(Int(1)) == Str("x")
    assert m.group(Int(2)) == Str("42")


def test_match_group_by_name() -> None:
    m = Re.match(Str(r"(?P<name>\w+)=(?P<value>\d+)"), Str("x=42"))
    assert isinstance(m, Match)
    assert m.group(Str("name")) == Str("x")
    assert m.group(Str("value")) == Str("42")


def test_match_group_multiple_returns_tuple() -> None:
    m = Re.match(Str(r"(\w+)=(\d+)"), Str("x=42"))
    assert isinstance(m, Match)
    out = m.group(Int(1), Int(2))
    assert isinstance(out, Tuple)
    assert out.at(Int(0)) == Str("x")
    assert out.at(Int(1)) == Str("42")


def test_match_groups() -> None:
    m = Re.match(Str(r"(\w+)=(\d+)"), Str("x=42"))
    assert isinstance(m, Match)
    gs = m.groups()
    assert isinstance(gs, Tuple)
    assert gs.at(Int(0)) == Str("x")
    assert gs.at(Int(1)) == Str("42")


def test_match_groups_missing_returns_none() -> None:
    m = Re.match(Str(r"(\w+)(?:=(\d+))?"), Str("x"))
    assert isinstance(m, Match)
    gs = m.groups()
    assert gs.at(Int(0)) == Str("x")
    assert gs.at(Int(1)) is none


def test_match_groupdict() -> None:
    m = Re.match(Str(r"(?P<name>\w+)=(?P<value>\d+)"), Str("x=42"))
    assert isinstance(m, Match)
    gd = m.groupdict()
    assert isinstance(gd, Dict)
    assert gd.at(Str("name")) == Str("x")
    assert gd.at(Str("value")) == Str("42")


def test_match_start_end_span() -> None:
    m = Re.search(Str(r"\d+"), Str("abc123def"))
    assert isinstance(m, Match)
    assert m.start() == Int(3)
    assert m.end() == Int(6)
    span = m.span()
    assert isinstance(span, Tuple)
    assert span.at(Int(0)) == Int(3)
    assert span.at(Int(1)) == Int(6)


def test_match_start_end_by_group() -> None:
    m = Re.match(Str(r"(\d+)"), Str("123"))
    assert isinstance(m, Match)
    assert m.start(Int(1)) == Int(0)
    assert m.end(Int(1)) == Int(3)


def test_match_expand() -> None:
    m = Re.match(Str(r"(\w+)=(\d+)"), Str("x=42"))
    assert isinstance(m, Match)
    assert m.expand(Str(r"\2-\1")) == Str("42-x")


def test_match_string_property() -> None:
    m = Re.match(Str(r"\d+"), Str("123abc"))
    assert isinstance(m, Match)
    assert m.string == Str("123abc")


def test_match_re_property() -> None:
    m = Re.match(Str(r"\d+"), Str("123abc"))
    assert isinstance(m, Match)
    assert isinstance(m.re, Pattern)
    assert m.re.pattern == Str(r"\d+")


def test_re_in_default_namespace() -> None:
    from poop.transformers import DEFAULT_NAMESPACE

    assert DEFAULT_NAMESPACE["re"] is Re
    assert DEFAULT_NAMESPACE["Pattern"] is Pattern
    assert DEFAULT_NAMESPACE["Match"] is Match


def test_re_reachable_via_interpreter() -> None:
    Interpreter().run_source('re.match("\\\\d+", "123").group().print()')


def test_re_error_exposed_for_try_except() -> None:
    """re.error is the exception raised on bad pattern compilation."""
    import re as _stdlib_re

    assert Re.error is _stdlib_re.error
    with pytest.raises(Re.error):
        Re.compile(Str("("))


def test_match_group_for_unmatched_optional_is_none() -> None:
    m = Re.match(Str(r"(\w+)(?:=(\d+))?"), Str("x"))
    assert isinstance(m, Match)
    assert m.group(Int(2)) is none
    assert isinstance(m.group(Int(2)), NoneClass)


# --- Try.except_ integration ---


def test_try_catches_invalid_regex() -> None:
    from poop.types.try_ import Try

    captured: list[object] = []
    Try(lambda: Re.compile(Str("("))).except_(
        Re.error, lambda e: captured.append(e.kind())
    ).run()
    assert len(captured) == 1


# --- purge / NOFLAG ---


def test_re_purge_returns_none() -> None:
    assert Re.purge() is none


def test_re_noflag_constant() -> None:
    assert isinstance(Re.NOFLAG, Int)
    assert Re.NOFLAG == Int(int(_re.NOFLAG))
