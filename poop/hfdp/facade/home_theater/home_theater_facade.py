from poop.hfdp.facade.home_theater.amplifier import Amplifier
from poop.hfdp.facade.home_theater.cd_player import CDPlayer
from poop.hfdp.facade.home_theater.popcorn_popper import PopcornPopper
from poop.hfdp.facade.home_theater.projector import Projector
from poop.hfdp.facade.home_theater.screen import Screen
from poop.hfdp.facade.home_theater.streaming_player import StreamingPlayer
from poop.hfdp.facade.home_theater.theater_lights import TheaterLights
from poop.hfdp.facade.home_theater.tuner import Tuner


class HomeTheaterFacade:
    def __init__(
        self,
        amp: Amplifier,
        tuner: Tuner,
        player: StreamingPlayer,
        cd: CDPlayer,
        projector: Projector,
        lights: TheaterLights,
        screen: Screen,
        pooper: PopcornPopper,
    ) -> None:
        self._amp = amp
        self._tuner = tuner
        self._player = player
        self._cd = cd
        self._projector = projector
        self._lights = lights
        self._screen = screen
        self._pooper = pooper

    def watch_movie(self, movie: str) -> None:
        print("Get ready to watch a movie...")
        self._pooper.on()
        self._pooper.pop()
        self._lights.dim(10)
        self._screen.down()
        self._projector.on()
        self._projector.wide_screen_mode()
        self._amp.on()
        self._amp.set_streaming_player(self._player)
        self._amp.set_surround_sound()
        self._amp.set_volume(5)
        self._player.on()
        self._player.play_movie(movie)

    def end_movie(self) -> None:
        print("Shutting movie theater down...")
        self._pooper.off()
        self._lights.on()
        self._screen.up()
        self._projector.off()
        self._amp.off()
        self._player.stop()
        self._player.off()

    def listen_to_radio(self, frequency: float) -> None:
        print("Tuning in the airwaves...")
        self._tuner.on()
        self._tuner.set_frequency(frequency)
        self._amp.on()
        self._amp.set_volume(5)
        self._amp.set_tuner(self._tuner)

    def end_radio(self) -> None:
        print("Shutting down the tuner...")
        self._tuner.off()
        self._amp.off()
