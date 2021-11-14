from poop.hfdp.command.party.light import Light


class LightOnCommand:
    def __init__(self, light: Light) -> None:
        self.light = light

    def execute(self) -> None:
        self.light.on()

    def undo(self) -> None:
        self.light.off()
