from poop.hfdp.facade.home_theater.streaming_player import StreamingPlayer


class Projector:
    def __init__(self, description: str, player: StreamingPlayer) -> None:
        self._description = description
        self._player = player

    def on(self) -> None:
        print(f"{self._description} on")

    def off(self) -> None:
        print(f"{self._description} off")

    def wide_screen_mode(self) -> None:
        print(f"{self._description} in widescreen mode (16x9 aspect ratio)")

    def tv_mode(self) -> None:
        print(f"{self._description} in tv mode (4x3 aspect ratio)")

    def __str__(self) -> str:
        return self._description
