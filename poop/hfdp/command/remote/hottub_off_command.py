from poop.hfdp.command.remote.hottub import Hottub


class HottubOffCommand:
    def __init__(self, hottub: Hottub) -> None:
        self.__hottub = hottub

    def execute(self) -> None:
        self.__hottub.cool()
        self.__hottub.off()
