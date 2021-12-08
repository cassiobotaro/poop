from poop.hfdp.factory.challenge.zone import Zone
from poop.hfdp.factory.challenge.zone_central import ZoneCentral
from poop.hfdp.factory.challenge.zone_eastern import ZoneEastern
from poop.hfdp.factory.challenge.zone_mountain import ZoneMountain
from poop.hfdp.factory.challenge.zone_pacific import ZonePacific


class ZoneFactory:
    def create_zone(self, zoneId: str) -> Zone | None:
        if zoneId == "US/Pacific":
            return ZonePacific()
        elif zoneId == "US/Mountain":
            return ZoneMountain()
        elif zoneId == "US/Central":
            return ZoneCentral()
        elif zoneId == "US/Eastern":
            return ZoneEastern()
        else:
            return None
