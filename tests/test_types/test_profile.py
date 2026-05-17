from __future__ import annotations

import tempfile
from pathlib import Path as _PyPath

from poop.interpreter import Interpreter
from poop.types.none import none
from poop.types.profile import CProfile, Profile, PStats, SortKey, Stats
from poop.types.string import Str


def _exercise(p: Profile) -> None:
    p.enable()
    sum(range(1000))
    p.disable()


def test_profile_constructs() -> None:
    assert isinstance(Profile(), Profile)


def test_profile_enable_disable_returns_none() -> None:
    p = Profile()
    assert p.enable() is none
    assert p.disable() is none


def test_profile_create_stats_returns_none() -> None:
    p = Profile()
    _exercise(p)
    assert p.create_stats() is none


def test_profile_print_stats_returns_str() -> None:
    p = Profile()
    _exercise(p)
    p.create_stats()
    text = p.print_stats()
    assert isinstance(text, Str)


def test_profile_dump_stats() -> None:
    p = Profile()
    _exercise(p)
    with tempfile.TemporaryDirectory() as td:
        out = _PyPath(td) / "profile.bin"
        assert p.dump_stats(Str(str(out))) is none
        assert out.exists()


def test_profile_runcall() -> None:
    p = Profile()
    result = p.runcall(lambda x, y: x + y, 1, 2)
    assert result == 3


def test_profile_context_manager() -> None:
    with Profile() as p:
        sum(range(100))
    text = p.print_stats()
    assert isinstance(text, Str)


def test_cprofile_run() -> None:
    with tempfile.TemporaryDirectory() as td:
        out = _PyPath(td) / "p.bin"
        assert CProfile.run(Str("sum(range(100))"), Str(str(out))) is none
        assert out.exists()


def test_cprofile_run_no_filename() -> None:
    assert CProfile.run(Str("sum(range(10))")) is none


def test_cprofile_class_attr() -> None:
    assert CProfile.Profile is Profile


# --- pstats ---


def test_stats_from_profile() -> None:
    p = Profile()
    _exercise(p)
    p.create_stats()
    s = Stats(p)
    assert isinstance(s, Stats)


def test_stats_sort_stats_returns_self() -> None:
    p = Profile()
    _exercise(p)
    s = Stats(p)
    assert s.sort_stats(SortKey.CUMULATIVE) is s


def test_stats_reverse_order_returns_self() -> None:
    p = Profile()
    _exercise(p)
    s = Stats(p)
    assert s.reverse_order() is s


def test_stats_strip_dirs_returns_self() -> None:
    p = Profile()
    _exercise(p)
    s = Stats(p)
    assert s.strip_dirs() is s


def test_stats_print_stats_returns_str() -> None:
    p = Profile()
    _exercise(p)
    s = Stats(p)
    assert isinstance(s.print_stats(), Str)


def test_stats_print_callers_returns_str() -> None:
    p = Profile()
    _exercise(p)
    s = Stats(p)
    assert isinstance(s.print_callers(), Str)


def test_stats_print_callees_returns_str() -> None:
    p = Profile()
    _exercise(p)
    s = Stats(p)
    assert isinstance(s.print_callees(), Str)


def test_stats_dump_stats() -> None:
    p = Profile()
    _exercise(p)
    s = Stats(p)
    with tempfile.TemporaryDirectory() as td:
        out = _PyPath(td) / "s.bin"
        assert s.dump_stats(Str(str(out))) is none
        assert out.exists()


def test_stats_add_extra_profile() -> None:
    p1 = Profile()
    _exercise(p1)
    p1.create_stats()
    p2 = Profile()
    _exercise(p2)
    p2.create_stats()
    s = Stats(p1)
    assert s.add(p2) is s


def test_stats_from_filename() -> None:
    p = Profile()
    _exercise(p)
    with tempfile.TemporaryDirectory() as td:
        out = _PyPath(td) / "p.bin"
        p.dump_stats(Str(str(out)))
        s = Stats(Str(str(out)))
        assert isinstance(s, Stats)


def test_sortkey_constants_are_str() -> None:
    assert isinstance(SortKey.CALLS, Str)
    assert isinstance(SortKey.CUMULATIVE, Str)
    assert isinstance(SortKey.FILENAME, Str)
    assert isinstance(SortKey.LINE, Str)
    assert isinstance(SortKey.NAME, Str)
    assert isinstance(SortKey.NFL, Str)
    assert isinstance(SortKey.PCALLS, Str)
    assert isinstance(SortKey.STDNAME, Str)
    assert isinstance(SortKey.TIME, Str)


def test_pstats_class_refs() -> None:
    assert PStats.Stats is Stats
    assert PStats.SortKey is SortKey


# --- Interpreter integration ---


def test_profile_via_interpreter() -> None:
    Interpreter().run_source(
        "p = Profile()\np.enable()\np.disable()\np.print_stats().print()"
    )
