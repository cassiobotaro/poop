from poop.hfdp.command.party.ceiling_fan import SPEED, CeilingFan


class CeilingFanOffCommand:
    def __init__(self, ceiling_fan: CeilingFan) -> None:
        self.__ceiling_fan = ceiling_fan
        self.__prev_speed = SPEED.OFF

    def execute(self) -> None:
        self.__prev_speed = self.__ceiling_fan.get_speed()
        self.__ceiling_fan.off()

    def undo(self) -> None:
        {
            SPEED.HIGH: self.__ceiling_fan.high,
            SPEED.MEDIUM: self.__ceiling_fan.medium,
            SPEED.LOW: self.__ceiling_fan.low,
            SPEED.OFF: self.__ceiling_fan.off,
        }[self.__prev_speed]()
