from poop.hfdp.command.party.light import Light


class LivingRoomLightOffCommand:
    def __init__(self, light: Light) -> None:
        self.__light = light

    def execute(self) -> None:
        self.__light.off()

    def undo(self) -> None:
        self.__light.on()
