import datetime as _datetime

import pytest

from poop.interpreter import Interpreter
from poop.types.datetime import (
    Date,
    DateTime,
    Datetime,
    Time,
    TimeDelta,
    TimeZone,
)
from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import none
from poop.types.string import Str


def test_date_basic_construction() -> None:
    d = Date(Int(2026), Int(5), Int(15))
    assert d.year == Int(2026)
    assert d.month == Int(5)
    assert d.day == Int(15)


def test_date_today_returns_date() -> None:
    assert isinstance(Date.today(), Date)


def test_date_fromisoformat() -> None:
    d = Date.fromisoformat(Str("2026-05-15"))
    assert d == Date(Int(2026), Int(5), Int(15))


def test_date_fromtimestamp() -> None:
    d = Date.fromtimestamp(Int(0))
    assert isinstance(d, Date)


def test_date_fromordinal() -> None:
    d = Date.fromordinal(Int(_datetime.date(2026, 1, 1).toordinal()))
    assert d == Date(Int(2026), Int(1), Int(1))


def test_date_weekday_isoweekday() -> None:
    d = Date(Int(2026), Int(5), Int(15))  # friday
    assert d.weekday() == Int(4)
    assert d.isoweekday() == Int(5)


def test_date_isoformat() -> None:
    assert Date(Int(2026), Int(5), Int(15)).isoformat() == Str("2026-05-15")


def test_date_strftime() -> None:
    assert Date(Int(2026), Int(5), Int(15)).strftime(Str("%Y/%m/%d")) == Str(
        "2026/05/15"
    )


def test_date_toordinal() -> None:
    assert Date(Int(2026), Int(1), Int(1)).toordinal() == Int(
        _datetime.date(2026, 1, 1).toordinal()
    )


def test_date_replace() -> None:
    d = Date(Int(2026), Int(5), Int(15))
    assert d.replace(year=Int(2027)) == Date(Int(2027), Int(5), Int(15))
    assert d.replace(day=Int(1)) == Date(Int(2026), Int(5), Int(1))


def test_date_add_timedelta() -> None:
    d = Date(Int(2026), Int(5), Int(15))
    assert d + TimeDelta(days=Int(7)) == Date(Int(2026), Int(5), Int(22))


def test_date_sub_timedelta() -> None:
    d = Date(Int(2026), Int(5), Int(15))
    assert d - TimeDelta(days=Int(15)) == Date(Int(2026), Int(4), Int(30))


def test_date_sub_date_returns_timedelta() -> None:
    diff = Date(Int(2026), Int(5), Int(22)) - Date(Int(2026), Int(5), Int(15))
    assert isinstance(diff, TimeDelta)
    assert diff.days == Int(7)


def test_date_equality_and_hash() -> None:
    a = Date(Int(2026), Int(1), Int(1))
    b = Date(Int(2026), Int(1), Int(1))
    assert a == b
    assert hash(a) == hash(b)


def test_time_basic_construction() -> None:
    t = Time(Int(12), Int(30), Int(45))
    assert t.hour == Int(12)
    assert t.minute == Int(30)
    assert t.second == Int(45)
    assert t.microsecond == Int(0)


def test_time_default_construction() -> None:
    t = Time()
    assert t.hour == Int(0)
    assert t.minute == Int(0)


def test_time_fromisoformat() -> None:
    t = Time.fromisoformat(Str("12:30:45"))
    assert t == Time(Int(12), Int(30), Int(45))


def test_time_isoformat() -> None:
    assert Time(Int(12), Int(30)).isoformat() == Str("12:30:00")


def test_time_strftime() -> None:
    assert Time(Int(12), Int(30)).strftime(Str("%H:%M")) == Str("12:30")


def test_time_tzinfo_none_returns_none() -> None:
    assert Time(Int(12)).tzinfo is none


def test_time_tzinfo_with_timezone() -> None:
    tz = TimeZone(TimeDelta(hours=Int(2)))
    t = Time(Int(12), tzinfo=tz)
    assert isinstance(t.tzinfo, TimeZone)


def test_time_replace() -> None:
    t = Time(Int(12), Int(30), Int(45))
    assert t.replace(hour=Int(13)) == Time(Int(13), Int(30), Int(45))


# replace(tzinfo=none) strips the timezone — proposal 118


def test_time_replace_tzinfo_none_strips() -> None:
    aware = Time(Int(10), Int(0), tzinfo=TimeZone.utc)
    assert aware.replace(tzinfo=none).tzinfo is none


def test_time_replace_omitting_tzinfo_keeps_it() -> None:
    aware = Time(Int(10), Int(0), tzinfo=TimeZone.utc)
    assert aware.replace(hour=Int(11)).tzinfo == TimeZone.utc


def test_datetime_replace_tzinfo_none_strips() -> None:
    aware = DateTime(Int(2024), Int(1), Int(1), Int(12), tzinfo=TimeZone.utc)
    assert aware.replace(tzinfo=none).tzinfo is none


def test_datetime_replace_omitting_tzinfo_keeps_it() -> None:
    aware = DateTime(Int(2024), Int(1), Int(1), Int(12), tzinfo=TimeZone.utc)
    assert aware.replace(hour=Int(6)).tzinfo == TimeZone.utc


def test_datetime_replace_tzinfo_wrapper_sets_it() -> None:
    naive = DateTime(Int(2024), Int(1), Int(1), Int(12))
    assert naive.replace(tzinfo=TimeZone.utc).tzinfo == TimeZone.utc


def test_datetime_basic_construction() -> None:
    dt = DateTime(Int(2026), Int(5), Int(15), Int(12), Int(30), Int(45))
    assert dt.year == Int(2026)
    assert dt.hour == Int(12)
    assert dt.minute == Int(30)


def test_datetime_now() -> None:
    assert isinstance(DateTime.now(), DateTime)


def test_datetime_now_with_tz() -> None:
    dt = DateTime.now(TimeZone.utc)
    assert isinstance(dt.tzinfo, TimeZone)


def test_datetime_utcnow() -> None:
    assert isinstance(DateTime.utcnow(), DateTime)


def test_datetime_fromtimestamp() -> None:
    dt = DateTime.fromtimestamp(Float(0.0), TimeZone.utc)
    assert dt.year == Int(1970)


def test_datetime_fromisoformat() -> None:
    dt = DateTime.fromisoformat(Str("2026-05-15T12:30:45"))
    assert dt == DateTime(Int(2026), Int(5), Int(15), Int(12), Int(30), Int(45))


def test_datetime_combine() -> None:
    d = Date(Int(2026), Int(5), Int(15))
    t = Time(Int(12), Int(30))
    dt = DateTime.combine(d, t)
    assert dt.year == Int(2026)
    assert dt.hour == Int(12)


def test_datetime_date_method() -> None:
    dt = DateTime(Int(2026), Int(5), Int(15), Int(12))
    assert dt.date() == Date(Int(2026), Int(5), Int(15))


def test_datetime_time_method() -> None:
    dt = DateTime(Int(2026), Int(5), Int(15), Int(12), Int(30))
    assert dt.time() == Time(Int(12), Int(30))


def test_datetime_timestamp() -> None:
    dt = DateTime(Int(1970), Int(1), Int(1), tzinfo=TimeZone.utc)
    assert dt.timestamp() == Float(0.0)


def test_datetime_isoformat() -> None:
    dt = DateTime(Int(2026), Int(5), Int(15), Int(12), Int(30))
    assert dt.isoformat() == Str("2026-05-15T12:30:00")


def test_datetime_isoformat_with_sep() -> None:
    dt = DateTime(Int(2026), Int(5), Int(15), Int(12))
    assert dt.isoformat(Str(" ")) == Str("2026-05-15 12:00:00")


def test_datetime_astimezone() -> None:
    dt = DateTime(Int(2026), Int(1), Int(1), tzinfo=TimeZone.utc)
    other = TimeZone(TimeDelta(hours=Int(-3)))
    converted = dt.astimezone(other)
    assert isinstance(converted, DateTime)


def test_datetime_replace() -> None:
    dt = DateTime(Int(2026), Int(5), Int(15), Int(12))
    new = dt.replace(year=Int(2027), hour=Int(8))
    assert new.year == Int(2027)
    assert new.hour == Int(8)
    assert new.month == Int(5)


def test_datetime_add_timedelta() -> None:
    dt = DateTime(Int(2026), Int(5), Int(15), Int(12))
    new = dt + TimeDelta(hours=Int(1))
    assert new.hour == Int(13)


def test_datetime_sub_timedelta() -> None:
    dt = DateTime(Int(2026), Int(5), Int(15), Int(12))
    new = dt - TimeDelta(hours=Int(1))
    assert isinstance(new, DateTime)
    assert new.hour == Int(11)


def test_datetime_sub_datetime_returns_timedelta() -> None:
    a = DateTime(Int(2026), Int(5), Int(15), Int(12))
    b = DateTime(Int(2026), Int(5), Int(15), Int(10))
    diff = a - b
    assert isinstance(diff, TimeDelta)
    assert diff.total_seconds() == Float(7200.0)


def test_datetime_comparisons() -> None:
    from poop.types.boolean import true

    a = DateTime(Int(2026), Int(1), Int(1))
    b = DateTime(Int(2026), Int(6), Int(1))
    assert (a < b) is true
    assert (b > a) is true
    assert (a <= a) is true
    assert (a >= a) is true


def test_timedelta_construction() -> None:
    td = TimeDelta(
        days=Int(1), seconds=Int(3600), microseconds=Int(0), milliseconds=Int(0)
    )
    assert td.days == Int(1)
    assert td.seconds == Int(3600)


def test_timedelta_total_seconds() -> None:
    td = TimeDelta(days=Int(1))
    assert td.total_seconds() == Float(86400.0)


def test_timedelta_add() -> None:
    a = TimeDelta(days=Int(1))
    b = TimeDelta(hours=Int(2))
    assert (a + b).total_seconds() == Float(86400.0 + 7200.0)


def test_timedelta_sub() -> None:
    a = TimeDelta(days=Int(2))
    b = TimeDelta(days=Int(1))
    assert (a - b).days == Int(1)


def test_timedelta_mul_int() -> None:
    td = TimeDelta(days=Int(1)) * Int(3)
    assert td.days == Int(3)


def test_timedelta_div_int() -> None:
    td = TimeDelta(days=Int(2)) / Int(2)
    assert isinstance(td, TimeDelta)
    assert td.days == Int(1)


def test_timedelta_div_timedelta_returns_float() -> None:
    out = TimeDelta(days=Int(2)) / TimeDelta(days=Int(1))
    assert isinstance(out, Float)
    assert out == Float(2.0)


def test_timedelta_floordiv_timedelta_returns_int() -> None:
    out = TimeDelta(days=Int(5)) // TimeDelta(days=Int(2))
    assert isinstance(out, Int)
    assert out == Int(2)


def test_timedelta_mod() -> None:
    out = TimeDelta(days=Int(5)) % TimeDelta(days=Int(2))
    assert isinstance(out, TimeDelta)
    assert out.days == Int(1)


def test_timedelta_neg() -> None:
    td = -TimeDelta(days=Int(1))
    assert isinstance(td, TimeDelta)


def test_timezone_construction() -> None:
    tz = TimeZone(TimeDelta(hours=Int(-3)), Str("BRT"))
    assert tz.tzname() == Str("BRT")


def test_timezone_default_name() -> None:
    tz = TimeZone(TimeDelta(hours=Int(-3)))
    assert isinstance(tz.tzname(), Str)


def test_timezone_utc_constant() -> None:
    assert isinstance(TimeZone.utc, TimeZone)
    assert TimeZone.utc.tzname() == Str("UTC")


def test_timezone_utcoffset() -> None:
    tz = TimeZone(TimeDelta(hours=Int(2)))
    offset = tz.utcoffset()
    assert isinstance(offset, TimeDelta)
    assert offset.total_seconds() == Float(7200.0)


def test_datetime_namespace_binds_classes() -> None:
    assert Datetime.date is Date
    assert Datetime.time is Time
    assert Datetime.datetime is DateTime
    assert Datetime.timedelta is TimeDelta
    assert Datetime.timezone is TimeZone


def test_datetime_in_default_namespace() -> None:
    from poop.transformers import DEFAULT_NAMESPACE

    assert DEFAULT_NAMESPACE["datetime"] is Datetime
    assert DEFAULT_NAMESPACE["Date"] is Date
    assert DEFAULT_NAMESPACE["Time"] is Time
    assert DEFAULT_NAMESPACE["DateTime"] is DateTime
    assert DEFAULT_NAMESPACE["TimeDelta"] is TimeDelta
    assert DEFAULT_NAMESPACE["TimeZone"] is TimeZone


def test_datetime_reachable_via_interpreter() -> None:
    Interpreter().run_source("Date(2026, 5, 15).isoformat().print()")


def test_invalid_date_raises() -> None:
    with pytest.raises(ValueError):
        Date(Int(2026), Int(13), Int(1))


def test_date_min_max_class_attributes() -> None:
    assert isinstance(Date.min, Date)
    assert isinstance(Date.max, Date)
    assert Date.min.year == Int(1)
    assert Date.max.year == Int(9999)


def test_date_min_max_via_interpreter() -> None:
    Interpreter().run_source("Date.max.year.print()")


# str/repr — proposal 126


def test_str_delegates_to_impl() -> None:
    assert str(Date(Int(2024), Int(1), Int(1))) == "2024-01-01"
    assert str(TimeDelta(days=Int(1), hours=Int(2))) == "1 day, 2:00:00"
    assert str(DateTime(Int(2024), Int(1), Int(1))) == "2024-01-01 00:00:00"
    assert str(Time(Int(10), Int(30))) == "10:30:00"
    assert str(TimeZone.utc) == "UTC"


def test_repr_delegates_to_str() -> None:
    assert repr(Date(Int(2024), Int(1), Int(1))) == "2024-01-01"
    assert repr(TimeDelta(days=Int(1))) == "1 day, 0:00:00"


# reflected timedelta arithmetic — proposal 116


def test_timedelta_plus_date_answers_date() -> None:
    r = TimeDelta(days=Int(1)) + Date(Int(2024), Int(1), Int(1))
    assert isinstance(r, Date)
    assert r == Date(Int(2024), Int(1), Int(2))


def test_timedelta_plus_datetime_answers_datetime() -> None:
    r = TimeDelta(hours=Int(1)) + DateTime(Int(2024), Int(1), Int(1))
    assert isinstance(r, DateTime)
    assert r == DateTime(Int(2024), Int(1), Int(1), Int(1))


def test_int_times_timedelta_via_rmul() -> None:
    r = Int(2) * TimeDelta(days=Int(1))
    assert isinstance(r, TimeDelta)
    assert r.days == Int(2)


def test_timedelta_add_foreign_is_notimplemented() -> None:
    assert TimeDelta(days=Int(1)).__add__(Int(1)) is NotImplemented
    assert TimeDelta(days=Int(1)).__sub__(Int(1)) is NotImplemented


# ordering — proposal 117


def test_date_ordering() -> None:
    from poop.types.boolean import false, true

    assert (Date(Int(2024), Int(1), Int(1)) < Date(Int(2024), Int(6), Int(1))) is true
    assert (Date(Int(2024), Int(6), Int(1)) <= Date(Int(2024), Int(6), Int(1))) is true
    assert (Date(Int(2024), Int(6), Int(1)) > Date(Int(2024), Int(1), Int(1))) is true
    assert (Date(Int(2024), Int(1), Int(1)) >= Date(Int(2024), Int(6), Int(1))) is false


def test_timedelta_ordering() -> None:
    from poop.types.boolean import true

    assert (TimeDelta(days=Int(1)) < TimeDelta(days=Int(2))) is true
    assert (TimeDelta(days=Int(2)) > TimeDelta(days=Int(1))) is true


def test_time_ordering() -> None:
    from poop.types.boolean import true

    assert (Time(Int(10), Int(0)) < Time(Int(11), Int(0))) is true
    assert (Time(Int(11), Int(0)) >= Time(Int(10), Int(0))) is true
