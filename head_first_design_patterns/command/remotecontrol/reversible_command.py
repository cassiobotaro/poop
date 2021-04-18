"""
Notes:
    - Undoable is an interface that defines what "undoable"
    should implement the undo method
    - Callable is an interface that defines what "callable"
    should implement the __call__ method
    - ReversibleCommand combines both interfaces
    - MacroCommand is just a ReversibleCommand Agreggator,
    it will consist of several commands that will be executed together
    - NoCommand is a null object command 9do nothing)
    - Commands will be used to decouple the invocator of a command from
    the objects that will actually perform the task.
"""
from abc import ABC, abstractmethod
from collections.abc import Callable

from equipament import TV, CeilingFan, Hottub, Light, Stereo


class Undoable(ABC):
    @abstractmethod
    def undo(self):
        raise NotImplementedError


class ReversibleCommand(Callable, Undoable):
    ...

    def __str__(self):
        return f"{self.__class__.__name__}"


class NoCommand(ReversibleCommand):
    def __call__(self):
        pass

    def undo(self):
        pass


class MacroCommand(ReversibleCommand):
    def __init__(self, commands: list[ReversibleCommand]):
        self._commands = commands

    def __call__(self):
        for command in self._commands:
            command()

    def undo(self):
        for command in reversed(self._commands):
            command.undo()


class LightOnCommand(ReversibleCommand):
    def __init__(self, light: Light):
        self.light = light

    def __call__(self):
        self.light.on()

    def undo(self):
        self.light.off()


class LightOffCommand(ReversibleCommand):
    def __init__(self, light: Light):
        self.light = light

    def __call__(self):
        self.light.off()

    def undo(self):
        self.light.on()


class TVOnCommand(ReversibleCommand):
    def __init__(self, tv: TV):
        self.tv = tv

    def __call__(self):
        self.tv.on()
        self.tv.set_input_channel()

    def undo(self):
        self.tv.off()


class TVOffCommand(ReversibleCommand):
    def __init__(self, tv: TV):
        self.tv = tv

    def __call__(self):
        self.tv.off()

    def undo(self):
        self.tv.on()


class HottubOffCommand(ReversibleCommand):
    def __init__(self, hottub: Hottub):
        self.hottub = hottub

    def __call__(self):
        self.hottub.set_temperature(98)
        self.hottub.off()

    def undo(self):
        self.hottub.on()


class HottubOnCommand(ReversibleCommand):
    def __init__(self, hottub: Hottub):
        self.hottub = hottub

    def __call__(self):
        self.hottub.on()
        self.hottub.set_temperature(104)
        self.hottub.circulate()

    def undo(self):
        self.hottub.off()


class StereoOnCommand(ReversibleCommand):
    def __init__(self, stereo: Stereo):
        self.stereo = stereo

    def __call__(self):
        self.stereo.on()

    def undo(self):
        self.stereo.off()


class StereoOffCommand(ReversibleCommand):
    def __init__(self, stereo: Stereo):
        self.stereo = stereo

    def __call__(self):
        self.stereo.off()

    def undo(self):
        self.stereo.on()


class CeilingFanHighCommand(ReversibleCommand):
    def __init__(self, ceiling_fan: CeilingFan):
        self.ceiling_fan = ceiling_fan
        self.previous_speed = self.ceiling_fan.SPEED.OFF

    def __call__(self):
        self.previous_speed = self.ceiling_fan.get_speed()
        self.ceiling_fan.high()

    def undo(self):
        {
            self.ceiling_fan.SPEED.HIGH: self.ceiling_fan.high,
            self.ceiling_fan.SPEED.MEDIUM: self.ceiling_fan.medium,
            self.ceiling_fan.SPEED.LOW: self.ceiling_fan.low,
            self.ceiling_fan.SPEED.OFF: self.ceiling_fan.off,
        }.get(self.previous_speed)()


class CeilingFanMediumCommand(ReversibleCommand):
    def __init__(self, ceiling_fan: CeilingFan):
        self.ceiling_fan = ceiling_fan
        self.previous_speed = self.ceiling_fan.SPEED.OFF

    def __call__(self):
        self.previous_speed = self.ceiling_fan.get_speed()
        self.ceiling_fan.medium()

    def undo(self):
        {
            self.ceiling_fan.SPEED.HIGH: self.ceiling_fan.high,
            self.ceiling_fan.SPEED.MEDIUM: self.ceiling_fan.medium,
            self.ceiling_fan.SPEED.LOW: self.ceiling_fan.low,
            self.ceiling_fan.SPEED.OFF: self.ceiling_fan.off,
        }.get(self.previous_speed)()


class CeilingFanLowCommand(ReversibleCommand):
    def __init__(self, ceiling_fan: CeilingFan):
        self.ceiling_fan = ceiling_fan
        self.previous_speed = self.ceiling_fan.SPEED.OFF

    def __call__(self):
        self.previous_speed = self.ceiling_fan.get_speed()
        self.ceiling_fan.low()

    def undo(self):
        {
            self.ceiling_fan.SPEED.HIGH: self.ceiling_fan.high,
            self.ceiling_fan.SPEED.MEDIUM: self.ceiling_fan.medium,
            self.ceiling_fan.SPEED.LOW: self.ceiling_fan.low,
            self.ceiling_fan.SPEED.OFF: self.ceiling_fan.off,
        }.get(self.previous_speed)()


class CeilingFanOffCommand(ReversibleCommand):
    def __init__(self, ceiling_fan: CeilingFan):
        self.ceiling_fan = ceiling_fan
        self.previous_speed = self.ceiling_fan.SPEED.OFF

    def __call__(self):
        self.previous_speed = self.ceiling_fan.get_speed()
        self.ceiling_fan.off()

    def undo(self):
        {
            self.ceiling_fan.SPEED.HIGH: self.ceiling_fan.high,
            self.ceiling_fan.SPEED.MEDIUM: self.ceiling_fan.medium,
            self.ceiling_fan.SPEED.LOW: self.ceiling_fan.low,
            self.ceiling_fan.SPEED.OFF: self.ceiling_fan.off,
        }.get(self.previous_speed)()
