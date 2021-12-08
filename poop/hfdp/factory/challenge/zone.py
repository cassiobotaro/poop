class Zone:
    def __init__(self) -> None:
        self._display_name = ""
        self._offset = 0

    def get_display_name(self) -> str:
        return self._display_name

    def get_offset(self) -> int:
        return self._offset
