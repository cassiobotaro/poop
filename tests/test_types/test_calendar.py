from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.calendar import Calendar, CalendarNamespace
from poop.types.datetime import Date
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- Module-level helpers ---


def test_isleap_2024() -> None:
    assert CalendarNamespace.isleap(Int(2024)) is true


def test_isleap_2023() -> None:
    assert CalendarNamespace.isleap(Int(2023)) is false


def test_leapdays_range() -> None:
    assert CalendarNamespace.leapdays(Int(2000), Int(2100)) == Int(25)


def test_weekday_known_date() -> None:
    # 2026-05-16 is a Saturday → 5
    assert CalendarNamespace.weekday(Int(2026), Int(5), Int(16)) == Int(5)


def test_monthrange_returns_tuple() -> None:
    result = CalendarNamespace.monthrange(Int(2026), Int(5))
    assert isinstance(result, Tuple)
    # May 2026 starts on a Friday (4) and has 31 days.
    assert result.at(Int(0)) == Int(4)
    assert result.at(Int(1)) == Int(31)


def test_monthcalendar_shape() -> None:
    result = CalendarNamespace.monthcalendar(Int(2026), Int(5))
    assert isinstance(result, List)
    first_week = result.at(Int(0))
    assert isinstance(first_week, List)


def test_month_renders_text() -> None:
    result = CalendarNamespace.month(Int(2026), Int(5))
    assert isinstance(result, Str)
    assert "May 2026" in result._value


def test_calendar_renders_year() -> None:
    result = CalendarNamespace.calendar(Int(2026))
    assert isinstance(result, Str)
    assert "2026" in result._value


def test_timegm_round_trip() -> None:
    # Epoch start: (1970, 1, 1, 0, 0, 0, 0, 0, 0) → 0
    t = Tuple(
        Int(1970),
        Int(1),
        Int(1),
        Int(0),
        Int(0),
        Int(0),
        Int(0),
        Int(0),
        Int(0),
    )
    assert CalendarNamespace.timegm(t) == Int(0)


# --- Constants ---


def test_weekday_constants() -> None:
    assert CalendarNamespace.MONDAY == Int(0)
    assert CalendarNamespace.SUNDAY == Int(6)


def test_month_constants() -> None:
    assert CalendarNamespace.JANUARY == Int(1)
    assert CalendarNamespace.DECEMBER == Int(12)


# --- Calendar class ---


def test_calendar_iterweekdays_default() -> None:
    cal = Calendar()
    days = cal.iterweekdays()
    assert isinstance(days, List)
    assert days == List(Int(0), Int(1), Int(2), Int(3), Int(4), Int(5), Int(6))


def test_calendar_iterweekdays_sunday_first() -> None:
    cal = Calendar(firstweekday=Int(6))
    days = cal.iterweekdays()
    assert days.at(Int(0)) == Int(6)


def test_calendar_itermonthdates_returns_dates() -> None:
    cal = Calendar()
    dates = cal.itermonthdates(Int(2026), Int(5))
    assert isinstance(dates, List)
    first = dates.at(Int(0))
    assert isinstance(first, Date)


def test_calendar_itermonthdays() -> None:
    cal = Calendar()
    days = cal.itermonthdays(Int(2026), Int(5))
    assert isinstance(days, List)
    # First few entries are 0 for days outside the month.
    for d in days:
        assert isinstance(d, Int)


def test_calendar_itermonthdays2_yields_pairs() -> None:
    cal = Calendar()
    entries = cal.itermonthdays2(Int(2026), Int(5))
    assert isinstance(entries, List)
    first = entries.at(Int(0))
    assert isinstance(first, Tuple)


def test_calendar_monthdatescalendar_shape() -> None:
    cal = Calendar()
    weeks = cal.monthdatescalendar(Int(2026), Int(5))
    assert isinstance(weeks, List)
    week = weeks.at(Int(0))
    assert isinstance(week, List)
    assert week.len() == Int(7)


# --- Interpreter integration ---


def test_calendar_isleap_reachable_via_interpreter() -> None:
    Interpreter().run_source("calendar.isleap(2024).print()")


def test_calendar_class_reachable_via_interpreter() -> None:
    Interpreter().run_source("Calendar().iterweekdays().len().print()")


def test_calendar_monthrange_reachable_via_interpreter() -> None:
    Interpreter().run_source("calendar.monthrange(2026, 5).print()")
