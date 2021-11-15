from poop.hfdp.command.simpleremote.light import Light


class LightOffCommand:
    def __init__(self, light: Light) -> None:
        self.__light = light

    def execute(self) -> None:
        self.__light.off()
