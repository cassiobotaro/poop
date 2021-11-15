from poop.hfdp.command.undo.light import Light


class DimmerLightOnCommand:
    def __init__(self, light: Light) -> None:
        self.light = light
        self.prev_level = Light.OFF_LEVEL

    def execute(self) -> None:
        self.prev_level = self.light.get_level()
        self.light.dim(75)

    def undo(self) -> None:
        self.light.dim(self.prev_level)
