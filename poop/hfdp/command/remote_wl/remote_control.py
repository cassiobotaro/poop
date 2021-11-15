from poop.hfdp.command.remote_wl.command import Command


class RemoteControl:
    def __init__(self) -> None:
        def no_command() -> None:
            pass

        self.__on_commands: list[Command] = [no_command for _ in range(7)]
        self.__off_commands: list[Command] = [no_command for _ in range(7)]

    def set_command(
        self, slot: int, on_command: Command, off_command: Command
    ) -> None:
        self.__on_commands[slot] = on_command
        self.__off_commands[slot] = off_command

    def on_button_was_pushed(self, slot: int) -> None:
        self.__on_commands[slot]()

    def off_button_was_pushed(self, slot: int) -> None:
        self.__off_commands[slot]()

    def __str__(self) -> str:
        title = "\n------ Remote Control ------\n"
        on_commands = self.__on_commands
        off_commands = self.__off_commands
        commands = "\n".join(
            f"[slot {index}] {on_commands[index].__qualname__} "
            f"{off_commands[index].__qualname__}"
            for index in range(7)
        )
        return f"{title}\n{commands}\n"
