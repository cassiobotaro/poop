from poop.hfdp.facade.home_theater.amplifier import Amplifier


class CDPlayer:
    def __init__(self, description: str, amplifier: Amplifier) -> None:
        self._description = description
        self._amplifier = amplifier
        self._current_track: int | None = None
        self._title: str | None = None

    def on(self) -> None:
        print(f"{self._description} on")

    def off(self) -> None:
        print(f"{self._description} off")

    def eject(self) -> None:
        self._title = None
        print(f"{self._description} eject")

    def play_title(self, title: str) -> None:
        self._title = title
        self._current_track = 0
        print(f"{self._description} playing '{self._title}'")

    def play_track(self, track: int) -> None:
        if self._title is None:
            print(
                f"{self._description} can't play track {track} "
                ", no cd inserted"
            )
        else:
            self._current_track = track
            print(f"{self._description} playing track {self._current_track}")

    def stop(self) -> None:
        self._current_track = 0
        print(f"{self._description} stopped")

    def pause(self) -> None:
        print(f"{self._description} paused {self._title}")

    def __str__(self) -> str:
        return self._description
