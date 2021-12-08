from poop.hfdp.factory.challenge.zone import Zone


class ZoneCentral(Zone):
    def __init__(self) -> None:
        self._display_name = "US/Central"
        self._offset = -6
