from home_theater import (
    Amplifier,
    CDPlayer,
    PopcornPopper,
    Projector,
    Screen,
    StreamingPlayer,
    TheaterLights,
    Tuner,
)
from home_theater_facade import HomeTheaterFacade

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
