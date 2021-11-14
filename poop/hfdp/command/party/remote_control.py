from poop.hfdp.command.party.command import Command
from poop.hfdp.command.party.nocommand import NoCommand


class RemoteControl:
    def __init__(self) -> None:
        no_command = NoCommand()
        self.__on_commands: list[Command] = [no_command for _ in range(7)]
        self.__off_commands: list[Command] = [no_command for _ in range(7)]
        self.__undo_command: Command = no_command

    def set_command(
        self, slot: int, on_command: Command, off_command: Command
    ) -> None:
        self.__on_commands[slot] = on_command
        self.__off_commands[slot] = off_command

    def on_button_was_pushed(self, slot: int) -> None:
        self.__on_commands[slot].execute()
        self.__undo_command = self.__on_commands[slot]

    def off_button_was_pushed(self, slot: int) -> None:
        self.__off_commands[slot].execute()
        self.__undo_command = self.__off_commands[slot]

    def undo_button_was_pushed(self) -> None:
        self.__undo_command.undo()

    def __str__(self) -> str:
        title = "\n------ Remote Control ------\n"
        on_commands = self.__on_commands
        off_commands = self.__off_commands
        commands = "\n".join(
            f"[slot {index}] {on_commands[index].__class__.__qualname__} "
            f"{off_commands[index].__class__.__qualname__}"
            for index in range(7)
        )
        undo = f"Undo: {self.__undo_command.__class__.__qualname__}"
        return f"{title}\n{commands}\n{undo}"
