from poop.hfdp.command.remote.light import Light


class LivingRoomLightOffCommand:
    def __init__(self, light: Light) -> None:
        self.__light = light

    def execute(self) -> None:
        self.__light.off()
