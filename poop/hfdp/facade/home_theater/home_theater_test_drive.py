from poop.hfdp.facade.home_theater.amplifier import Amplifier
from poop.hfdp.facade.home_theater.cd_player import CDPlayer
from poop.hfdp.facade.home_theater.home_theater_facade import HomeTheaterFacade
from poop.hfdp.facade.home_theater.popcorn_popper import PopcornPopper
from poop.hfdp.facade.home_theater.projector import Projector
from poop.hfdp.facade.home_theater.screen import Screen
from poop.hfdp.facade.home_theater.streaming_player import StreamingPlayer
from poop.hfdp.facade.home_theater.theater_lights import TheaterLights
from poop.hfdp.facade.home_theater.tuner import Tuner


def main() -> None:
    amp = Amplifier("Amplifier")
    tuner = Tuner("AM/FM Tuner", amp)
    player = StreamingPlayer("Streaming Player", amp)
    cd = CDPlayer("CD Player", amp)
    projector = Projector("Projector", player)
    lights = TheaterLights("Theater Ceiling Lights")
    screen = Screen("Theater Screen")
    popper = PopcornPopper("Popcorn Popper")

    home_theater = HomeTheaterFacade(
        amp, tuner, player, cd, projector, lights, screen, popper
    )
    home_theater.watch_movie("The Matrix")
    home_theater.end_movie()
