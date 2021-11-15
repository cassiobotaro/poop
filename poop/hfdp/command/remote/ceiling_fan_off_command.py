from poop.hfdp.command.remote.ceiling_fan import CeilingFan


class CeilingFanOffCommand:
    def __init__(self, ceiling_fan: CeilingFan) -> None:
        self.__ceiling_fan = ceiling_fan

    def execute(self) -> None:
        self.__ceiling_fan.off()
