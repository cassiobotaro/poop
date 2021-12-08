from poop.hfdp.factory.challenge.calendar import Calendar
from poop.hfdp.factory.challenge.zone_factory import ZoneFactory


class PacificCalendar(Calendar):
    def __init__(self, zone_factory: ZoneFactory) -> None:
        self._zone = zone_factory.create_zone("US/Pacific")

    def create_calendar(self, appointments: list[str]) -> None:
        print(f"Making the calendar with appts: {appointments}")
