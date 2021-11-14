from poop.hfdp.command.party.light import Light


class LivingRoomLightOnCommand:
    def __init__(self, light: Light) -> None:
        self.__light = light

    def execute(self) -> None:
        self.__light.on()

    def undo(self) -> None:
        self.__light.off()
