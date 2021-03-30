from equipament import TV, Hottub, Light, Stereo
from reversible_command import (
    HottubOffCommand,
    HottubOnCommand,
    LightOffCommand,
    LightOnCommand,
    MacroCommand,
    NoCommand,
    ReversibleCommand,
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

    def set_command(
        self,
        slot: int,
        on_command: ReversibleCommand,
        off_command: ReversibleCommand,
    ):
        self._on_commands[slot] = on_command
        self._off_commands[slot] = off_command

    def on_button_was_pushed(self, slot: int):
        command = self._on_commands[slot]
        command()
        self._undo_command = command

    def off_button_was_pushed(self, slot: int):
        command = self._off_commands[slot]
        command()
        self._undo_command = command

    def undo_button_was_pushed(self):
        self._undo_command()

    def __str__(self) -> str:
        title = "\n------ Remote Control ------\n"
        commands = "\n".join(
            f"[slot {index}] {self._on_commands[index].__name__}"
            f"{self._off_commands[index].__name__}"
            for index in range(7)
        )
        undo = self._undo_command.__name__
        return f"{title}{commands}{undo}"


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
