from poop.types.calendar import (
    Calendar,
    CalendarNamespace,
    HTMLCalendar,
    LocaleHTMLCalendar,
    LocaleTextCalendar,
    TextCalendar,
)

NAMESPACE: dict[str, object] = {
    "calendar": CalendarNamespace,
    "Calendar": Calendar,
    "TextCalendar": TextCalendar,
    "HTMLCalendar": HTMLCalendar,
    "LocaleTextCalendar": LocaleTextCalendar,
    "LocaleHTMLCalendar": LocaleHTMLCalendar,
}
