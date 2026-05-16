import calendar as _calendar
from typing import ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.datetime import Date
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str
from poop.types.tuple import Tuple


def _i(value: Int | None, default: int) -> int:
    return default if value is None else value._value


class Calendar:
    """Wraps Python's `calendar.Calendar` for date iteration.

    `Calendar(firstweekday=0)` configures which day starts the week
    (`0`=Monday, `6`=Sunday). The `iter*` methods return materialised
    POOP `List`s — POOP collections are not lazy.
    """

    __slots__ = ("_impl",)

    def __init__(self, firstweekday: Int | None = None) -> None:
        self._impl = _calendar.Calendar(_i(firstweekday, 0))

    def iterweekdays(self) -> List:
        return List(*(Int(d) for d in self._impl.iterweekdays()))

    def itermonthdates(self, year: Int, month: Int) -> List:
        return List(
            *(
                Date._from_impl(d)
                for d in self._impl.itermonthdates(year._value, month._value)
            )
        )

    def itermonthdays(self, year: Int, month: Int) -> List:
        return List(
            *(Int(d) for d in self._impl.itermonthdays(year._value, month._value))
        )

    def itermonthdays2(self, year: Int, month: Int) -> List:
        return List(
            *(
                Tuple(Int(day), Int(wd))
                for day, wd in self._impl.itermonthdays2(year._value, month._value)
            )
        )

    def itermonthdays3(self, year: Int, month: Int) -> List:
        return List(
            *(
                Tuple(Int(y), Int(m), Int(d))
                for y, m, d in self._impl.itermonthdays3(year._value, month._value)
            )
        )

    def monthdatescalendar(self, year: Int, month: Int) -> List:
        return List(
            *(
                List(*(Date._from_impl(d) for d in week))
                for week in self._impl.monthdatescalendar(year._value, month._value)
            )
        )

    def monthdayscalendar(self, year: Int, month: Int) -> List:
        return List(
            *(
                List(*(Int(d) for d in week))
                for week in self._impl.monthdayscalendar(year._value, month._value)
            )
        )

    def yeardatescalendar(self, year: Int, width: Int | None = None) -> List:
        return List(
            *(
                List(
                    *(
                        List(
                            *(
                                List(*(Date._from_impl(d) for d in week))
                                for week in month
                            )
                        )
                        for month in row
                    )
                )
                for row in self._impl.yeardatescalendar(year._value, _i(width, 3))
            )
        )


class CalendarNamespace:
    """Namespace mirroring Python's `calendar` module.

    Module-level shortcuts (`isleap`, `leapdays`, `weekday`,
    `monthrange`, `monthcalendar`, `month`, `calendar`, `timegm`)
    plus the weekday constants (`MONDAY` … `SUNDAY`). The reusable
    `Calendar` class is exposed alongside this namespace.

    `HTMLCalendar`, `LocaleTextCalendar`, and `LocaleHTMLCalendar`
    are out of scope for v1 (niche output formats).
    """

    MONDAY: ClassVar[Int] = Int(_calendar.MONDAY)
    TUESDAY: ClassVar[Int] = Int(_calendar.TUESDAY)
    WEDNESDAY: ClassVar[Int] = Int(_calendar.WEDNESDAY)
    THURSDAY: ClassVar[Int] = Int(_calendar.THURSDAY)
    FRIDAY: ClassVar[Int] = Int(_calendar.FRIDAY)
    SATURDAY: ClassVar[Int] = Int(_calendar.SATURDAY)
    SUNDAY: ClassVar[Int] = Int(_calendar.SUNDAY)

    JANUARY: ClassVar[Int] = Int(_calendar.JANUARY)
    FEBRUARY: ClassVar[Int] = Int(_calendar.FEBRUARY)
    MARCH: ClassVar[Int] = Int(_calendar.MARCH)
    APRIL: ClassVar[Int] = Int(_calendar.APRIL)
    MAY: ClassVar[Int] = Int(_calendar.MAY)
    JUNE: ClassVar[Int] = Int(_calendar.JUNE)
    JULY: ClassVar[Int] = Int(_calendar.JULY)
    AUGUST: ClassVar[Int] = Int(_calendar.AUGUST)
    SEPTEMBER: ClassVar[Int] = Int(_calendar.SEPTEMBER)
    OCTOBER: ClassVar[Int] = Int(_calendar.OCTOBER)
    NOVEMBER: ClassVar[Int] = Int(_calendar.NOVEMBER)
    DECEMBER: ClassVar[Int] = Int(_calendar.DECEMBER)

    IllegalMonthError: ClassVar[type[Exception]] = _calendar.IllegalMonthError
    IllegalWeekdayError: ClassVar[type[Exception]] = _calendar.IllegalWeekdayError

    @staticmethod
    def isleap(year: Int) -> Boolean:
        return true if _calendar.isleap(year._value) else false

    @staticmethod
    def leapdays(y1: Int, y2: Int) -> Int:
        return Int(_calendar.leapdays(y1._value, y2._value))

    @staticmethod
    def weekday(year: Int, month: Int, day: Int) -> Int:
        return Int(_calendar.weekday(year._value, month._value, day._value))

    @staticmethod
    def monthrange(year: Int, month: Int) -> Tuple:
        first, ndays = _calendar.monthrange(year._value, month._value)
        return Tuple(Int(first), Int(ndays))

    @staticmethod
    def monthcalendar(year: Int, month: Int) -> List:
        return List(
            *(
                List(*(Int(d) for d in week))
                for week in _calendar.monthcalendar(year._value, month._value)
            )
        )

    @staticmethod
    def month(
        year: Int,
        month: Int,
        w: Int | None = None,
        l: Int | None = None,  # noqa: E741 — matches CPython's calendar.month signature
    ) -> Str:
        return Str(_calendar.month(year._value, month._value, _i(w, 0), _i(l, 0)))

    @staticmethod
    def calendar(
        year: Int,
        w: Int | None = None,
        l: Int | None = None,  # noqa: E741 — matches CPython's calendar.calendar signature
        c: Int | None = None,
        m: Int | None = None,
    ) -> Str:
        return Str(
            _calendar.calendar(year._value, _i(w, 2), _i(l, 1), _i(c, 6), _i(m, 3))
        )

    @staticmethod
    def timegm(time_tuple: Tuple) -> Int:
        # `time_tuple` is a 9-element struct_time-shaped POOP Tuple.
        unwrapped: list[int] = []
        for item in time_tuple:
            if not isinstance(item, Int):
                raise TypeError(
                    f"timegm tuple entries must be Int, got {type(item).__name__}"
                )
            unwrapped.append(item._value)
        return Int(_calendar.timegm(tuple(unwrapped)))
