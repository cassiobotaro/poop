from poop.hfdp.command.simpleremote.command import Command


class SimpleRemoteControl:
    def __init__(self) -> None:
        self.slot: Command | None = None

    def set_command(self, command: Command) -> None:
        self.slot = command

    def button_was_pressed(self) -> None:
        if self.slot:
            self.slot.execute()
