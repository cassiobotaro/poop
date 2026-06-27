from __future__ import annotations

import datetime as _datetime
import zoneinfo as _zoneinfo
from typing import TYPE_CHECKING, Any, ClassVar

from poop.types._impl_wrapper import _ImplWrapperMixin
from poop.types._unwrap import _unwrap
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import Boolean, to_boolean
from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str

if TYPE_CHECKING:
    from poop.types.zoneinfo import ZoneInfo


def _opt_tz(tz: TimeZone | ZoneInfo | NoneClass | None) -> _datetime.tzinfo | None:
    if tz is None or isinstance(tz, NoneClass):
        return None
    return tz._impl


class _AbsentType:
    """Sentinel for `replace(tzinfo=...)` so the three cases stay distinct:
    argument omitted (keep current tzinfo), explicit POOP `none` (strip to
    naive), or a wrapper (set it). A bare default of `none` cannot express
    'strip', leaving aware values unable to ever become naive."""

    __slots__ = ()


_ABSENT = _AbsentType()


def _replace_tz(
    tzinfo: TimeZone | ZoneInfo | NoneClass | _AbsentType,
    current: _datetime.tzinfo | None,
) -> _datetime.tzinfo | None:
    if isinstance(tzinfo, _AbsentType):
        return current  # argument omitted -> keep current tzinfo
    if isinstance(tzinfo, NoneClass):
        return None  # explicit none -> strip to naive
    return tzinfo._impl  # wrapper -> set the tzinfo


class _StrReprMixin:
    """`__str__`/`__repr__` delegating to the wrapped stdlib `self._impl`.

    Mirrors how every other value wrapper (Decimal, Fraction, UUID, the
    ipaddress family) prints, so `.print()` and the REPL show the value
    (`2024-01-01`, `1 day, 2:00:00`) instead of `Object`'s `<Date>`.
    """

    __slots__ = ()

    _impl: Any

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class _OrderedImplMixin:
    """Total ordering for wrappers exposing a comparable `self._impl`.

    `Date`, `Time`, `TimeDelta`, and `DateTime` all order against another
    instance of the same kind via their stdlib `_impl`.
    """

    __slots__ = ()

    _impl: Any

    def __lt__(self, other: Any) -> Boolean:
        return to_boolean(self._impl < other._impl)

    def __le__(self, other: Any) -> Boolean:
        return to_boolean(self._impl <= other._impl)

    def __gt__(self, other: Any) -> Boolean:
        return to_boolean(self._impl > other._impl)

    def __ge__(self, other: Any) -> Boolean:
        return to_boolean(self._impl >= other._impl)


class TimeDelta(
    _StrReprMixin, _OrderedImplMixin, _ImplWrapperMixin, _ValueEqMixin, Object
):
    """Wraps Python's `datetime.timedelta` — a duration."""

    __slots__ = ("_impl",)
    _eq_attr: ClassVar[str] = "_impl"

    def __init__(
        self,
        days: Int | Float | NoneClass | None = None,
        seconds: Int | Float | NoneClass | None = None,
        microseconds: Int | Float | NoneClass | None = None,
        milliseconds: Int | Float | NoneClass | None = None,
        minutes: Int | Float | NoneClass | None = None,
        hours: Int | Float | NoneClass | None = None,
        weeks: Int | Float | NoneClass | None = None,
    ) -> None:
        self._impl = _datetime.timedelta(
            days=_unwrap(days, 0),
            seconds=_unwrap(seconds, 0),
            microseconds=_unwrap(microseconds, 0),
            milliseconds=_unwrap(milliseconds, 0),
            minutes=_unwrap(minutes, 0),
            hours=_unwrap(hours, 0),
            weeks=_unwrap(weeks, 0),
        )

    @property
    def days(self) -> Int:
        return Int(self._impl.days)

    @property
    def seconds(self) -> Int:
        return Int(self._impl.seconds)

    @property
    def microseconds(self) -> Int:
        return Int(self._impl.microseconds)

    def total_seconds(self) -> Float:
        return Float(self._impl.total_seconds())

    def __add__(self, other: object) -> TimeDelta:
        # Only timedelta + timedelta is a TimeDelta. For Date/DateTime
        # operands return NotImplemented so their __radd__ answers a
        # Date/DateTime instead of a corrupted TimeDelta shell.
        if not isinstance(other, TimeDelta):
            return NotImplemented
        return TimeDelta._from_impl(self._impl + other._impl)

    def __sub__(self, other: object) -> TimeDelta:
        if not isinstance(other, TimeDelta):
            return NotImplemented
        return TimeDelta._from_impl(self._impl - other._impl)

    def __mul__(self, other: Int | Float) -> TimeDelta:
        return TimeDelta._from_impl(self._impl * other._value)

    # timedelta * n and n * timedelta are both valid in Python.
    __rmul__ = __mul__

    def __truediv__(self, other: Int | Float | TimeDelta) -> TimeDelta | Float:
        if isinstance(other, TimeDelta):
            return Float(self._impl / other._impl)
        return TimeDelta._from_impl(self._impl / other._value)

    def __floordiv__(self, other: Int | TimeDelta) -> TimeDelta | Int:
        if isinstance(other, TimeDelta):
            return Int(self._impl // other._impl)
        return TimeDelta._from_impl(self._impl // other._value)

    def __mod__(self, other: TimeDelta) -> TimeDelta:
        return TimeDelta._from_impl(self._impl % other._impl)

    def __neg__(self) -> TimeDelta:
        return TimeDelta._from_impl(-self._impl)

    def __hash__(self) -> int:
        return hash(self._impl)


class TimeZone(_StrReprMixin, _ImplWrapperMixin, _ValueEqMixin, Object):
    """Wraps Python's `datetime.timezone` — a fixed UTC offset."""

    __slots__ = ("_impl",)
    _eq_attr: ClassVar[str] = "_impl"

    utc: ClassVar[TimeZone]

    def __init__(
        self,
        offset: TimeDelta,
        name: Str | NoneClass | None = None,
    ) -> None:
        n = _unwrap(name, None)
        if n is None:
            self._impl = _datetime.timezone(offset._impl)
        else:
            self._impl = _datetime.timezone(offset._impl, n)

    def utcoffset(self, dt: DateTime | NoneClass | None = None) -> TimeDelta:
        impl_dt: _datetime.datetime | None = None
        if dt is not None and not isinstance(dt, NoneClass):
            impl_dt = dt._impl
        return TimeDelta._from_impl(self._impl.utcoffset(impl_dt))

    def tzname(self, dt: DateTime | NoneClass | None = None) -> Str:
        impl_dt: _datetime.datetime | None = None
        if dt is not None and not isinstance(dt, NoneClass):
            impl_dt = dt._impl
        return Str(self._impl.tzname(impl_dt))

    def __hash__(self) -> int:
        return hash(self._impl)


TimeZone.utc = TimeZone._from_impl(_datetime.UTC)


class _DateFieldsMixin:
    """Calendar fields shared by `Date` and `DateTime` — both forward
    to a stdlib `_impl` exposing the date API."""

    __slots__ = ()

    _impl: Any

    @property
    def year(self) -> Int:
        return Int(self._impl.year)

    @property
    def month(self) -> Int:
        return Int(self._impl.month)

    @property
    def day(self) -> Int:
        return Int(self._impl.day)

    def weekday(self) -> Int:
        return Int(self._impl.weekday())

    def isoweekday(self) -> Int:
        return Int(self._impl.isoweekday())


class _TimeFieldsMixin:
    """Clock fields shared by `Time` and `DateTime` — both forward to
    a stdlib `_impl` exposing the time API."""

    __slots__ = ()

    _impl: Any

    @property
    def hour(self) -> Int:
        return Int(self._impl.hour)

    @property
    def minute(self) -> Int:
        return Int(self._impl.minute)

    @property
    def second(self) -> Int:
        return Int(self._impl.second)

    @property
    def microsecond(self) -> Int:
        return Int(self._impl.microsecond)

    @property
    def tzinfo(self) -> TimeZone | ZoneInfo | NoneClass:
        from poop.types.zoneinfo import ZoneInfo as _ZoneInfo

        tz = self._impl.tzinfo
        if tz is None:
            return none
        if isinstance(tz, _datetime.timezone):
            return TimeZone._from_impl(tz)
        if isinstance(tz, _zoneinfo.ZoneInfo):
            return _ZoneInfo._from_impl(tz)
        return none


class Date(
    _StrReprMixin,
    _OrderedImplMixin,
    _DateFieldsMixin,
    _ImplWrapperMixin,
    _ValueEqMixin,
    Object,
):
    """Wraps Python's `datetime.date`."""

    __slots__ = ("_impl",)
    _eq_attr: ClassVar[str] = "_impl"

    min: ClassVar[Date]
    max: ClassVar[Date]

    def __init__(self, year: Int, month: Int, day: Int) -> None:
        self._impl = _datetime.date(year._value, month._value, day._value)

    @classmethod
    def today(cls) -> Date:
        return cls._from_impl(_datetime.date.today())

    @classmethod
    def fromisoformat(cls, s: Str) -> Date:
        return cls._from_impl(_datetime.date.fromisoformat(s._value))

    @classmethod
    def fromtimestamp(cls, t: Int | Float) -> Date:
        return cls._from_impl(_datetime.date.fromtimestamp(t._value))

    @classmethod
    def fromordinal(cls, n: Int) -> Date:
        return cls._from_impl(_datetime.date.fromordinal(n._value))

    def isoformat(self) -> Str:
        return Str(self._impl.isoformat())

    def strftime(self, fmt: Str) -> Str:
        return Str(self._impl.strftime(fmt._value))

    def toordinal(self) -> Int:
        return Int(self._impl.toordinal())

    def replace(
        self,
        year: Int | NoneClass | None = None,
        month: Int | NoneClass | None = None,
        day: Int | NoneClass | None = None,
    ) -> Date:
        return Date._from_impl(
            self._impl.replace(
                year=_unwrap(year, self._impl.year),
                month=_unwrap(month, self._impl.month),
                day=_unwrap(day, self._impl.day),
            )
        )

    def __add__(self, other: TimeDelta) -> Date:
        return Date._from_impl(self._impl + other._impl)

    # Reached when a TimeDelta is on the left (timedelta + date); date
    # addition commutes, so reuse __add__.
    def __radd__(self, other: TimeDelta) -> Date:
        return self.__add__(other)

    def __sub__(self, other: Date | TimeDelta) -> Date | TimeDelta:
        if isinstance(other, TimeDelta):
            return Date._from_impl(self._impl - other._impl)
        return TimeDelta._from_impl(self._impl - other._impl)

    def __hash__(self) -> int:
        return hash(self._impl)


Date.min = Date._from_impl(_datetime.date.min)
Date.max = Date._from_impl(_datetime.date.max)


class Time(
    _StrReprMixin,
    _OrderedImplMixin,
    _TimeFieldsMixin,
    _ImplWrapperMixin,
    _ValueEqMixin,
    Object,
):
    """Wraps Python's `datetime.time`."""

    __slots__ = ("_impl",)
    _eq_attr: ClassVar[str] = "_impl"

    def __init__(
        self,
        hour: Int | NoneClass | None = None,
        minute: Int | NoneClass | None = None,
        second: Int | NoneClass | None = None,
        microsecond: Int | NoneClass | None = None,
        tzinfo: TimeZone | ZoneInfo | NoneClass | None = None,
    ) -> None:
        self._impl = _datetime.time(
            hour=_unwrap(hour, 0),
            minute=_unwrap(minute, 0),
            second=_unwrap(second, 0),
            microsecond=_unwrap(microsecond, 0),
            tzinfo=_opt_tz(tzinfo),
        )

    @classmethod
    def fromisoformat(cls, s: Str) -> Time:
        return cls._from_impl(_datetime.time.fromisoformat(s._value))

    def isoformat(self, timespec: Str | NoneClass | None = None) -> Str:
        from poop.types._unwrap import _opt_str

        return Str(self._impl.isoformat(_opt_str(timespec, "auto")))

    def strftime(self, fmt: Str) -> Str:
        return Str(self._impl.strftime(fmt._value))

    def replace(
        self,
        hour: Int | NoneClass | None = None,
        minute: Int | NoneClass | None = None,
        second: Int | NoneClass | None = None,
        microsecond: Int | NoneClass | None = None,
        tzinfo: TimeZone | ZoneInfo | NoneClass | _AbsentType = _ABSENT,
    ) -> Time:
        kwargs: dict[str, Any] = {
            "hour": _unwrap(hour, self._impl.hour),
            "minute": _unwrap(minute, self._impl.minute),
            "second": _unwrap(second, self._impl.second),
            "microsecond": _unwrap(microsecond, self._impl.microsecond),
            "tzinfo": _replace_tz(tzinfo, self._impl.tzinfo),
        }
        return Time._from_impl(self._impl.replace(**kwargs))

    def __hash__(self) -> int:
        return hash(self._impl)


class DateTime(
    _StrReprMixin,
    _OrderedImplMixin,
    _DateFieldsMixin,
    _TimeFieldsMixin,
    _ImplWrapperMixin,
    _ValueEqMixin,
    Object,
):
    """Wraps Python's `datetime.datetime`."""

    __slots__ = ("_impl",)
    _eq_attr: ClassVar[str] = "_impl"

    def __init__(
        self,
        year: Int,
        month: Int,
        day: Int,
        hour: Int | NoneClass | None = None,
        minute: Int | NoneClass | None = None,
        second: Int | NoneClass | None = None,
        microsecond: Int | NoneClass | None = None,
        tzinfo: TimeZone | ZoneInfo | NoneClass | None = None,
    ) -> None:
        self._impl = _datetime.datetime(
            year._value,
            month._value,
            day._value,
            _unwrap(hour, 0),
            _unwrap(minute, 0),
            _unwrap(second, 0),
            _unwrap(microsecond, 0),
            _opt_tz(tzinfo),
        )

    @classmethod
    def now(cls, tz: TimeZone | ZoneInfo | NoneClass | None = None) -> DateTime:
        return cls._from_impl(_datetime.datetime.now(_opt_tz(tz)))

    @classmethod
    def utcnow(cls) -> DateTime:
        return cls._from_impl(_datetime.datetime.now(_datetime.UTC))

    @classmethod
    def fromtimestamp(
        cls, t: Int | Float, tz: TimeZone | ZoneInfo | NoneClass | None = None
    ) -> DateTime:
        return cls._from_impl(_datetime.datetime.fromtimestamp(t._value, _opt_tz(tz)))

    @classmethod
    def fromisoformat(cls, s: Str) -> DateTime:
        return cls._from_impl(_datetime.datetime.fromisoformat(s._value))

    @classmethod
    def combine(
        cls,
        date: Date,
        time: Time,
        tzinfo: TimeZone | ZoneInfo | NoneClass | _AbsentType = _ABSENT,
    ) -> DateTime:
        # Omitted (_ABSENT) keeps the time's tzinfo, matching CPython's
        # `tzinfo=self.tzinfo` default; an explicit POOP `none` strips it
        # to a naive datetime. A bare `none` default could not tell those
        # two cases apart.
        if isinstance(tzinfo, _AbsentType):
            tz = time._impl.tzinfo
        else:
            tz = _opt_tz(tzinfo)
        return cls._from_impl(_datetime.datetime.combine(date._impl, time._impl, tz))

    def date(self) -> Date:
        return Date._from_impl(self._impl.date())

    def time(self) -> Time:
        return Time._from_impl(self._impl.time())

    def timestamp(self) -> Float:
        return Float(self._impl.timestamp())

    def astimezone(self, tz: TimeZone | ZoneInfo | NoneClass | None = None) -> DateTime:
        return DateTime._from_impl(self._impl.astimezone(_opt_tz(tz)))

    def isoformat(
        self,
        sep: Str | NoneClass | None = None,
        timespec: Str | NoneClass | None = None,
    ) -> Str:
        from poop.types._unwrap import _opt_str

        return Str(self._impl.isoformat(_unwrap(sep, "T"), _opt_str(timespec, "auto")))

    def strftime(self, fmt: Str) -> Str:
        return Str(self._impl.strftime(fmt._value))

    def replace(
        self,
        year: Int | NoneClass | None = None,
        month: Int | NoneClass | None = None,
        day: Int | NoneClass | None = None,
        hour: Int | NoneClass | None = None,
        minute: Int | NoneClass | None = None,
        second: Int | NoneClass | None = None,
        microsecond: Int | NoneClass | None = None,
        tzinfo: TimeZone | ZoneInfo | NoneClass | _AbsentType = _ABSENT,
    ) -> DateTime:
        kwargs: dict[str, Any] = {
            "year": _unwrap(year, self._impl.year),
            "month": _unwrap(month, self._impl.month),
            "day": _unwrap(day, self._impl.day),
            "hour": _unwrap(hour, self._impl.hour),
            "minute": _unwrap(minute, self._impl.minute),
            "second": _unwrap(second, self._impl.second),
            "microsecond": _unwrap(microsecond, self._impl.microsecond),
            "tzinfo": _replace_tz(tzinfo, self._impl.tzinfo),
        }
        return DateTime._from_impl(self._impl.replace(**kwargs))

    def __add__(self, other: TimeDelta) -> DateTime:
        return DateTime._from_impl(self._impl + other._impl)

    # Reached when a TimeDelta is on the left (timedelta + datetime).
    def __radd__(self, other: TimeDelta) -> DateTime:
        return self.__add__(other)

    def __sub__(self, other: DateTime | TimeDelta) -> DateTime | TimeDelta:
        if isinstance(other, TimeDelta):
            return DateTime._from_impl(self._impl - other._impl)
        return TimeDelta._from_impl(self._impl - other._impl)

    def __hash__(self) -> int:
        return hash(self._impl)


class Datetime:
    """Namespace mirroring Python's `datetime` module — binds the
    five wrapper classes as module attributes."""

    date: ClassVar[type[Date]] = Date
    time: ClassVar[type[Time]] = Time
    datetime: ClassVar[type[DateTime]] = DateTime
    timedelta: ClassVar[type[TimeDelta]] = TimeDelta
    timezone: ClassVar[type[TimeZone]] = TimeZone
