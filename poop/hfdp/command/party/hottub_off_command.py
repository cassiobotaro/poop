from poop.hfdp.command.party.hottub import Hottub


class HottubOffCommand:
    def __init__(self, hottub: Hottub) -> None:
        self.__hottub = hottub

    def execute(self) -> None:
        self.__hottub.set_temperature(98)
        self.__hottub.off()

    def undo(self) -> None:
        self.__hottub.on()
