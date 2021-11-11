from typing import Optional


class Tuner:
    def __init__(self, description: str, amp: "Amplifier") -> None:
        self.description = description
        self.amplifier: "Amplifier" = amp
        self.frequency: float = 0.0

    def on(self) -> None:
        print(self.description + " on")

    def off(self) -> None:
        print(self.description + " off")

    def set_frequency(self, frequency: float) -> None:
        print(f"{self.description} setting frequency to {frequency}")
        self.frequency = frequency

    def set_am(self) -> None:
        print(f"{self.description} setting AM mode")

    def set_fm(self) -> None:
        print(f"{self.description} setting FM mode")

    def __str__(self) -> str:
        return self.description


class StreamingPlayer:
    def __init__(self, description: str, amplifier: "Amplifier") -> None:
        self.description = description
        self.amplifier = amplifier
        self.current_chapter: Optional[int] = None
        self.movie: Optional[str] = None

    def on(self) -> None:
        print(self.description + " on")

    def off(self) -> None:
        print(self.description + " off")

    def play_movie(self, movie: str) -> None:
        self.movie = movie
        self.current_chapter = 0
        print(f"{self.description} playing '{self.movie}'")

    def play_chapter(self, chapter: int) -> None:
        if self.movie is None:
            print(
                f"{self.description} can't play chapter {chapter} "
                "no movie selected"
            )
        else:
            self.current_chapter = chapter
            print(
                f"{self.description} playing chapter {chapter} of {self.movie}"
            )

    def stop(self) -> None:
        self.current_chapter = 0
        print(f"{self.description} stopped {self.movie}")

    def pause(self) -> None:
        print(f"{self.description} paused {self.movie}")

    def set_two_channel_audio(self) -> None:
        print(f"{self.description} set two channel audio")

    def set_surround_audio(self) -> None:
        print(f"{self.description} set surround audio")

    def __str__(self) -> str:
        return self.description


class Amplifier:
    def __init__(self, description: str) -> None:
        self.description = description
        self.tuner: Optional[Tuner] = None
        self.player: Optional[StreamingPlayer] = None

    def on(self) -> None:
        print(f"{self.description} on")

    def off(self) -> None:
        print(f"{self.description} off")

    def set_stereo_sound(self) -> None:
        print(f"{self.description} stereo mode on")

    def set_surround_sound(self) -> None:
        print(f"{self.description} surround mode on (5 speakers, 1 subwoofer)")

    def set_volume(self, volume: int) -> None:
        print(f"{self.description} setting volume to {volume}")

    def set_tuner(self, tuner: Tuner) -> None:
        print(f"{self.description} setting tuner to {self.player}")
        self.tuner = tuner

    def set_streaming_player(
        self, streaming_player: "StreamingPlayer"
    ) -> None:
        print(f"{self.description} setting streaming player to {self.player}")
        self.streaming_player = streaming_player

    def __str__(self) -> str:
        return self.description


class CDPlayer:
    def __init__(self, description: str, amplifier: Amplifier) -> None:
        self.description = description
        self.amplifier = amplifier
        self.current_track: Optional[int] = None
        self.title: Optional[str] = None

    def on(self) -> None:
        print(f"{self.description} on")

    def off(self) -> None:
        print(f"{self.description} off")

    def eject(self) -> None:
        self.title = None
        print(f"{self.description} eject")

    def play_title(self, title: str) -> None:
        self.title = title
        self.current_track = 0
        print(f"{self.description} playing '{self.title}'")

    def play_track(self, track: int) -> None:
        if self.title is None:
            print(
                f"{self.description} can't play track {track} "
                ", no cd inserted"
            )
        else:
            self.current_track = track
            print(f"{self.description} playing track {self.current_track}")

    def stop(self) -> None:
        self.current_track = 0
        print(f"{self.description} stopped")

    def pause(self) -> None:
        print(f"{self.description} paused {self.title}")

    def __str__(self) -> str:
        return self.description


class TheaterLights:
    def __init__(self, description: str) -> None:
        self.description = description

    def on(self) -> None:
        print(f"{self.description} on")

    def off(self) -> None:
        print(f"{self.description} off")

    def dim(self, level: int) -> None:
        print(f"{self.description} dimming to {level}%")

    def __str__(self) -> str:
        return self.description


class Screen:
    def __init__(self, description: str) -> None:
        self.description = description

    def up(self) -> None:
        print(f"{self.description} going up")

    def down(self) -> None:
        print(f"{self.description} going down")

    def __str__(self) -> str:
        return self.description


class Projector:
    def __init__(self, description: str, player: StreamingPlayer) -> None:
        self.description = description
        self.player = player

    def on(self) -> None:
        print(f"{self.description} on")

    def off(self) -> None:
        print(f"{self.description} off")

    def wide_screen_mode(self) -> None:
        print(f"{self.description} in widescreen mode (16x9 aspect ratio)")

    def tv_mode(self) -> None:
        print(f"{self.description} in tv mode (4x3 aspect ratio)")

    def __str__(self) -> str:
        return self.description


class PopcornPopper:
    def __init__(self, description: str) -> None:
        self.description = description

    def on(self) -> None:
        print(f"{self.description} on")

    def off(self) -> None:
        print(f"{self.description} off")

    def pop(self) -> None:
        print(f"{self.description} popping popcorn!")

    def __str__(self) -> str:
        return self.description
