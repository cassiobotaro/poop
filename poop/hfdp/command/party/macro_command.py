from poop.hfdp.command.party.command import Command


class MacroCommand:
    def __init__(self, commands: list[Command]) -> None:
        self.__commands = commands

    def execute(self) -> None:
        for command in self.__commands:
            command.execute()

    def undo(self) -> None:
        for command in reversed(self.__commands):
            command.undo()
