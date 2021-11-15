from poop.hfdp.command.undo.ceiling_fan import SPEED, CeilingFan


class CeilingFanMediumCommand:
    def __init__(self, ceiling_fan: CeilingFan) -> None:
        self.ceiling_fan = ceiling_fan
        self.prev_speed = SPEED.OFF

    def execute(self) -> None:
        self.prev_speed = self.ceiling_fan.get_speed()
        self.ceiling_fan.medium()

    def undo(self) -> None:
        {
            SPEED.HIGH: self.ceiling_fan.high,
            SPEED.MEDIUM: self.ceiling_fan.medium,
            SPEED.LOW: self.ceiling_fan.low,
            SPEED.OFF: self.ceiling_fan.off,
        }[self.prev_speed]()
