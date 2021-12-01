from poop.hfdp.facade.home_theater.streaming_player import StreamingPlayer
from poop.hfdp.facade.home_theater.tuner import Tuner


class Amplifier:
    def __init__(self, description: str) -> None:
        self._description = description
        self._tuner: Tuner | None = None
        self._player: StreamingPlayer | None = None

    def on(self) -> None:
        print(f"{self._description} on")

    def off(self) -> None:
        print(f"{self._description} off")

    def set_stereo_sound(self) -> None:
        print(f"{self._description} stereo mode on")

    def set_surround_sound(self) -> None:
        print(
            f"{self._description} surround mode on (5 speakers, 1 subwoofer)"
        )

    def set_volume(self, volume: int) -> None:
        print(f"{self._description} setting volume to {volume}")

    def set_tuner(self, tuner: Tuner) -> None:
        print(f"{self._description} setting tuner to {self._player}")
        self._tuner = tuner

    def set_streaming_player(
        self, streaming_player: "StreamingPlayer"
    ) -> None:
        print(
            f"{self._description} setting streaming player to {self._player}"
        )
        self.streaming_player = streaming_player

    def __str__(self) -> str:
        return self._description
