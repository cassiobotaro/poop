from poop.hfdp.command.party.stereo import Stereo


class StereoOnWithCDCommand:
    def __init__(self, stereo: Stereo) -> None:
        self.__stereo = stereo

    def execute(self) -> None:
        self.__stereo.on()
        self.__stereo.set_cd()
        self.__stereo.set_volume(11)

    def undo(self) -> None:
        self.__stereo.off()
