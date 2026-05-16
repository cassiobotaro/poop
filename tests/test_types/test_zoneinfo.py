import pytest

from poop.interpreter import Interpreter
from poop.types.datetime import DateTime
from poop.types.int import Int
from poop.types.none import none
from poop.types.set import Set
from poop.types.string import Str
from poop.types.tuple import Tuple
from poop.types.zoneinfo import ZoneInfo, Zoneinfo

# --- ZoneInfo class ---


def test_zoneinfo_construction_by_key() -> None:
    tz = ZoneInfo(Str("America/Sao_Paulo"))
    assert isinstance(tz, ZoneInfo)


def test_zoneinfo_key_property() -> None:
    tz = ZoneInfo(Str("UTC"))
    assert tz.key == Str("UTC")


def test_zoneinfo_unknown_raises() -> None:
    with pytest.raises(Zoneinfo.ZoneInfoNotFoundError):
        ZoneInfo(Str("Not/A/Real_Zone_Foo"))


def test_zoneinfo_no_cache_returns_fresh() -> None:
    tz = ZoneInfo.no_cache(Str("UTC"))
    assert isinstance(tz, ZoneInfo)
    assert tz.key == Str("UTC")


def test_zoneinfo_clear_cache_returns_none() -> None:
    assert ZoneInfo.clear_cache() is none


def test_zoneinfo_clear_cache_only_keys() -> None:
    ZoneInfo(Str("UTC"))
    assert ZoneInfo.clear_cache(Set(Str("UTC"))) is none


# --- Module-level helpers ---


def test_available_timezones_returns_set_of_str() -> None:
    zones = Zoneinfo.available_timezones()
    assert isinstance(zones, Set)
    assert zones.includes(Str("UTC"))


def test_tzpath_returns_tuple_of_str() -> None:
    path = Zoneinfo.TZPATH()
    assert isinstance(path, Tuple)


def test_reset_tzpath_default() -> None:
    assert Zoneinfo.reset_tzpath() is none


def test_reset_tzpath_with_paths() -> None:
    # Pass an empty path tuple to reset to no system zones; then
    # restore the default for subsequent tests.
    assert Zoneinfo.reset_tzpath(Tuple()) is none
    Zoneinfo.reset_tzpath()


# --- Integration with datetime ---


def test_zoneinfo_works_with_datetime_now() -> None:
    tz = ZoneInfo(Str("UTC"))
    dt = DateTime.now(tz)
    # The wrapped tzinfo should be a ZoneInfo on the underlying impl.
    assert dt._impl.tzinfo is tz._impl


def test_zoneinfo_works_with_datetime_astimezone() -> None:
    dt = DateTime.now(ZoneInfo(Str("UTC")))
    converted = dt.astimezone(ZoneInfo(Str("America/Sao_Paulo")))
    assert converted._impl.tzinfo is not None


def test_zoneinfo_works_with_datetime_constructor() -> None:
    dt = DateTime(
        Int(2026),
        Int(5),
        Int(16),
        Int(12),
        Int(0),
        tzinfo=ZoneInfo(Str("UTC")),
    )
    assert dt._impl.tzinfo is not None


# --- Interpreter integration ---


def test_zoneinfo_class_reachable_via_interpreter() -> None:
    Interpreter().run_source('ZoneInfo("UTC").key.print()')


def test_zoneinfo_available_timezones_reachable_via_interpreter() -> None:
    Interpreter().run_source('zoneinfo.available_timezones().includes("UTC").print()')
