from poop.hfdp.command.remote.garage_door import GarageDoor


class GarageDoorDownCommand:
    def __init__(self, garage_door: GarageDoor) -> None:
        self.__garage_door = garage_door

    def execute(self) -> None:
        self.__garage_door.down()
