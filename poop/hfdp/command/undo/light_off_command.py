from poop.hfdp.command.undo.light import Light


class LightOffCommand:
    def __init__(self, light: Light) -> None:
        self.light = light
        self.level = Light.OFF_LEVEL

    def execute(self) -> None:
        self.level = self.light.get_level()
        self.light.off()

    def undo(self) -> None:
        self.light.dim(self.level)
