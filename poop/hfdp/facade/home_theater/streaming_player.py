import typing

if typing.TYPE_CHECKING:
    from poop.hfdp.facade.home_theater.amplifier import Amplifier


class StreamingPlayer:
    def __init__(self, description: str, amplifier: "Amplifier") -> None:
        self._description = description
        self._amplifier = amplifier
        self._current_chapter: int | None = None
        self._movie: str | None = None

    def on(self) -> None:
        print(self._description + " on")

    def off(self) -> None:
        print(self._description + " off")

    def play_movie(self, movie: str) -> None:
        self._movie = movie
        self._current_chapter = 0
        print(f"{self._description} playing '{self._movie}'")

    def play_chapter(self, chapter: int) -> None:
        if self._movie is None:
            print(
                f"{self._description} can't play chapter {chapter} "
                "no movie selected"
            )
        else:
            self._current_chapter = chapter
            print(
                f"{self._description} playing chapter {chapter} "
                f"of {self._movie}"
            )

    def stop(self) -> None:
        self._current_chapter = 0
        print(f"{self._description} stopped {self._movie}")

    def pause(self) -> None:
        print(f"{self._description} paused {self._movie}")

    def set_two_channel_audio(self) -> None:
        print(f"{self._description} set two channel audio")

    def set_surround_audio(self) -> None:
        print(f"{self._description} set surround audio")

    def __str__(self) -> str:
        return self._description
