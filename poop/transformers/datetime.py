from poop.types.datetime import Date, DateTime, Datetime, Time, TimeDelta, TimeZone

NAMESPACE: dict[str, object] = {
    "datetime": Datetime,
    "Date": Date,
    "Time": Time,
    "DateTime": DateTime,
    "TimeDelta": TimeDelta,
    "TimeZone": TimeZone,
}
