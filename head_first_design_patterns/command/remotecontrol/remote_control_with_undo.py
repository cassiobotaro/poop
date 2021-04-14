from equipament import TV, Hottub, Light, Stereo, CeilingFan
from reversible_command import (
    HottubOffCommand,
    HottubOnCommand,
    LightOffCommand,
    LightOnCommand,
    MacroCommand,
    NoCommand,
    StereoOffCommand,
    StereoOnCommand,
    TVOffCommand,
    TVOnCommand,
    CeilingFanMediumCommand,
    CeilingFanHighCommand,
    CeilingFanLowCommand,
    CeilingFanOffCommand,
)


class RemoteControl:
    def __init__(self):
        self._on_commands = [NoCommand() for _ in range(7)]
        self._off_commands = [NoCommand() for _ in range(7)]
        self._undo_command = NoCommand()

    def set_command(self, slot, on_command, off_command):
        self._on_commands[slot] = on_command
        self._off_commands[slot] = off_command

    def on_button_was_pushed(self, slot):
        command = self._on_commands[slot]
        command()
        self._undo_command = command

    def off_button_was_pushed(self, slot):
        command = self._off_commands[slot]
        command()
        self._undo_command = command

    def undo_button_was_pushed(self):
        self._undo_command.undo()

    def __str__(self) -> str:
        title = "\n------ Remote Control ------\n"
        commands = "\n".join(
            f"[slot {index}] {self._on_commands[index]} "
            f"{self._off_commands[index]}"
            for index in range(7)
        )
        undo = f"Undo: {self._undo_command}"
        return f"{title}\n{commands}\n{undo}"


if __name__ == "__main__":
    remote_control = RemoteControl()

    living_room_light = Light("Living Room")

    remote_control.set_command(
        0,
        LightOnCommand(living_room_light),
        LightOffCommand(living_room_light),
    )

    remote_control.on_button_was_pushed(0)
    remote_control.off_button_was_pushed(0)
    print(remote_control)
    remote_control.undo_button_was_pushed()
    remote_control.off_button_was_pushed(0)
    remote_control.on_button_was_pushed(0)
    print(remote_control)
    remote_control.undo_button_was_pushed()

    ceiling_fan = CeilingFan("Living room")
    ceiling_fan_medium_command = CeilingFanMediumCommand(ceiling_fan)
    ceiling_fan_high_command = CeilingFanHighCommand(ceiling_fan)
    ceiling_fan_low_command = CeilingFanLowCommand(ceiling_fan)
    ceiling_fan_off_command = CeilingFanOffCommand(ceiling_fan)

    remote_control.set_command(
        1, CeilingFanLowCommand(ceiling_fan), CeilingFanOffCommand(ceiling_fan)
    )
    remote_control.set_command(
        2,
        CeilingFanMediumCommand(ceiling_fan),
        CeilingFanOffCommand(ceiling_fan),
    )
    remote_control.set_command(
        3,
        CeilingFanHighCommand(ceiling_fan),
        CeilingFanOffCommand(ceiling_fan),
    )

    print("---")
    remote_control.on_button_was_pushed(1)
    remote_control.off_button_was_pushed(1)
    print(remote_control)
    remote_control.undo_button_was_pushed()
    remote_control.on_button_was_pushed(2)
    remote_control.on_button_was_pushed(3)
    remote_control.undo_button_was_pushed()
