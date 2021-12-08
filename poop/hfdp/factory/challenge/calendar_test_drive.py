from poop.hfdp.factory.challenge.pacific_calendar import PacificCalendar
from poop.hfdp.factory.challenge.zone_factory import ZoneFactory


def main() -> None:
    zone_factory = ZoneFactory()
    calendar = PacificCalendar(zone_factory)
    appts = ["appt 1", "appt 2"]
    calendar.create_calendar(appts)
    calendar.print()
