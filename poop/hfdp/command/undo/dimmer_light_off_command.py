from poop.hfdp.command.undo.light import Light


class DimmerLightOffCommand:
    def __init__(self, light: Light) -> None:
        self.light = light
        self.prev_level = Light.ON_LEVEL

    def execute(self) -> None:
        self.prev_level = self.light.get_level()
        self.light.off()

    def undo(self) -> None:
        self.light.dim(self.prev_level)
