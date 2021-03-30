from typing import Protocol
from equipament import Light, TV, Hottub, Stereo


class ReversibleCommand(Protocol):
    def __call__(self):
        ...

    def undo(self):
        ...


class NoCommand:
    def __call__(self):
        pass

    def undo(self):
        pass


class MacroCommand:
    def __init__(self, commands: list[ReversibleCommand]):
        self._commands = commands

    def __call__(self):
        for command in self._commands:
            command()

    def undo(self):
        for command in reversed(self._commands):
            command.undo()


class LightOnCommand:
    def __init__(self, light: Light):
        self.light = light

    def __call__(self):
        self.light.on()

    def undo(self):
        self.light.off()


class LightOffCommand:
    def __init__(self, light: Light):
        self.light = light

    def __call__(self):
        self.light.off()

    def undo(self):
        self.light.on()


class TVOnCommand:
    def __init__(self, tv: TV):
        self.tv = tv

    def __call__(self):
        self.tv.on()
        self.tv.set_input_channel()

    def undo(self):
        self.tv.off()


class TVOffCommand:
    def __init__(self, tv: TV):
        self.tv = tv

    def __call__(self):
        self.tv.off()

    def undo(self):
        self.tv.on()


class HottubOffCommand:
    def __init__(self, hottub: Hottub):
        self.hottub = hottub

    def __call__(self):
        self.hottub.set_temperature(98)
        self.hottub.off()

    def undo(self):
        self.hottub.on()


class HottubOnCommand:
    def __init__(self, hottub: Hottub):
        self.hottub = hottub

    def __call__(self):
        self.hottub.on()
        self.hottub.set_temperature(104)
        self.hottub.circulate()

    def undo(self):
        self.hottub.off()


class StereoOnCommand:
    def __init__(self, stereo: Stereo):
        self.stereo = stereo

    def __call__(self):
        self.stereo.on()

    def undo(self):
        self.stereo.off()


class StereoOffCommand:
    def __init__(self, stereo: Stereo):
        self.stereo = stereo

    def __call__(self):
        self.stereo.off()

    def undo(self):
        self.stereo.on()
