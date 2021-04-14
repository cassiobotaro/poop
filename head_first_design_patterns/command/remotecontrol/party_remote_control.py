from equipament import TV, Hottub, Light, Stereo
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
    light = Light("Living Room")
    tv = TV("Living Room")
    stereo = Stereo("Living Room")
    hottub = Hottub()

    party_on = [
        LightOnCommand(light),
        StereoOnCommand(stereo),
        TVOnCommand(tv),
        HottubOnCommand(hottub),
    ]
    party_off = [
        LightOffCommand(light),
        StereoOffCommand(stereo),
        TVOffCommand(tv),
        HottubOffCommand(hottub),
    ]

    remote_control = RemoteControl()
    remote_control.set_command(
        0, MacroCommand(party_on), MacroCommand(party_off)
    )

    print(remote_control)
    print("--- Pushing Macro On ---")
    remote_control.on_button_was_pushed(0)
    print("--- Pushing Macro Off ---")
    remote_control.off_button_was_pushed(0)
