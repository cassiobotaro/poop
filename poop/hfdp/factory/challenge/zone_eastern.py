from poop.hfdp.factory.challenge.zone import Zone


class ZoneEastern(Zone):
    def __init__(self) -> None:
        self._display_name = "US/Eastern"
        self._offset = -5
