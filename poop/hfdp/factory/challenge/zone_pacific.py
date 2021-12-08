from poop.hfdp.factory.challenge.zone import Zone


class ZonePacific(Zone):
    def __init__(self) -> None:
        self._display_name = "US/Pacific"
        self._offset = -8
