from poop.hfdp.command.party.tv import TV


class TVOnCommand:
    def __init__(self, tv: TV):
        self.__tv = tv

    def execute(self) -> None:
        self.__tv.on()
        self.__tv.set_input_channel()

    def undo(self) -> None:
        self.__tv.off()
