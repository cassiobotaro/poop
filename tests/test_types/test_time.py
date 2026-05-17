from poop.interpreter import Interpreter
from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import none
from poop.types.string import Str
from poop.types.time import StructTime, Time
from poop.types.tuple import Tuple

# --- Clocks ---


def test_time_returns_float() -> None:
    assert isinstance(Time.time(), Float)


def test_time_ns_returns_int() -> None:
    assert isinstance(Time.time_ns(), Int)


def test_monotonic_returns_float() -> None:
    assert isinstance(Time.monotonic(), Float)


def test_monotonic_ns_returns_int() -> None:
    assert isinstance(Time.monotonic_ns(), Int)


def test_perf_counter_returns_float() -> None:
    assert isinstance(Time.perf_counter(), Float)


def test_perf_counter_ns_returns_int() -> None:
    assert isinstance(Time.perf_counter_ns(), Int)


def test_process_time_returns_float() -> None:
    assert isinstance(Time.process_time(), Float)


def test_process_time_ns_returns_int() -> None:
    assert isinstance(Time.process_time_ns(), Int)


def test_thread_time_returns_float() -> None:
    assert isinstance(Time.thread_time(), Float)


def test_thread_time_ns_returns_int() -> None:
    assert isinstance(Time.thread_time_ns(), Int)


# --- Sleep ---


def test_sleep_returns_none() -> None:
    assert Time.sleep(Float(0)) is none


def test_sleep_accepts_int() -> None:
    assert Time.sleep(Int(0)) is none


# --- Format / parse ---


def test_strftime_default() -> None:
    assert isinstance(Time.strftime(Str("%Y")), Str)


def test_strftime_with_struct() -> None:
    t = Time.gmtime()
    assert isinstance(Time.strftime(Str("%Y"), t), Str)


def test_strptime_returns_structtime() -> None:
    t = Time.strptime(Str("2024"), Str("%Y"))
    assert isinstance(t, StructTime)
    assert t.tm_year == Int(2024)


def test_gmtime_no_args() -> None:
    assert isinstance(Time.gmtime(), StructTime)


def test_gmtime_with_secs() -> None:
    assert isinstance(Time.gmtime(Float(0)), StructTime)


def test_localtime_no_args() -> None:
    assert isinstance(Time.localtime(), StructTime)


def test_localtime_with_secs() -> None:
    assert isinstance(Time.localtime(Float(0)), StructTime)


def test_mktime_round_trip() -> None:
    t = Time.localtime(Float(1000000))
    assert isinstance(Time.mktime(t), Float)


def test_asctime_no_args() -> None:
    assert isinstance(Time.asctime(), Str)


def test_asctime_with_struct() -> None:
    t = Time.gmtime()
    assert isinstance(Time.asctime(t), Str)


def test_ctime_no_args() -> None:
    assert isinstance(Time.ctime(), Str)


def test_ctime_with_secs() -> None:
    assert isinstance(Time.ctime(Float(0)), Str)


# --- StructTime properties ---


def test_structtime_all_props_are_int() -> None:
    t = Time.gmtime(Float(0))  # epoch — 1970-01-01 00:00:00 UTC
    assert t.tm_year == Int(1970)
    assert t.tm_mon == Int(1)
    assert t.tm_mday == Int(1)
    assert t.tm_hour == Int(0)
    assert t.tm_min == Int(0)
    assert t.tm_sec == Int(0)
    assert isinstance(t.tm_wday, Int)
    assert isinstance(t.tm_yday, Int)
    assert isinstance(t.tm_isdst, Int)


def test_structtime_tm_zone_and_gmtoff() -> None:
    t = Time.gmtime(Float(0))
    # On most platforms these are present.
    zone = t.tm_zone
    gmtoff = t.tm_gmtoff
    assert isinstance(zone, Str) or zone is none
    assert isinstance(gmtoff, Int) or gmtoff is none


def test_structtime_repr() -> None:
    t = Time.gmtime(Float(0))
    assert "time.struct_time" in repr(t)


# --- Timezone info ---


def test_tzname_returns_tuple_of_str() -> None:
    tz = Time.tzname()
    assert isinstance(tz, Tuple)
    assert tz.len() == Int(2)


def test_timezone_altzone_daylight_are_ints() -> None:
    assert isinstance(Time.timezone(), Int)
    assert isinstance(Time.altzone(), Int)
    assert isinstance(Time.daylight(), Int)


def test_time_class_ref() -> None:
    assert Time.StructTime is StructTime


# --- Interpreter integration ---


def test_time_via_interpreter() -> None:
    Interpreter().run_source("time.time().print()")
