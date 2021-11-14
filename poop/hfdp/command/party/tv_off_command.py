from poop.hfdp.command.party.tv import TV


class TVOffCommand:
    def __init__(self, tv: TV):
        self.__tv = tv

    def execute(self) -> None:
        self.__tv.off()

    def undo(self) -> None:
        self.__tv.on()
