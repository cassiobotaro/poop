from poop.hfdp.command.party.hottub import Hottub


class HottubOnCommand:
    def __init__(self, hottub: Hottub) -> None:
        self.__hottub = hottub

    def execute(self) -> None:
        self.__hottub.on()
        self.__hottub.set_temperature(104)
        self.__hottub.circulate()

    def undo(self) -> None:
        self.__hottub.off()
