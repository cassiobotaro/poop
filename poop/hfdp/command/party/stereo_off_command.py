from poop.hfdp.command.party.stereo import Stereo


class StereoOffCommand:
    def __init__(self, stereo: Stereo) -> None:
        self.__stereo = stereo

    def execute(self) -> None:
        self.__stereo.off()

    def undo(self) -> None:
        self.__stereo.on()
