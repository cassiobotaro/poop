from poop.hfdp.command.remote.hottub import Hottub


class HottubOnCommand:
    def __init__(self, hottub: Hottub) -> None:
        self.__hottub = hottub

    def execute(self) -> None:
        self.__hottub.on()
        self.__hottub.heat()
        self.__hottub.bubbles_on()
