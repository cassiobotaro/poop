"""
Facade — one friendly door in front of a busy subsystem

Starting a movie really means powering a projector, dropping the
screen, waking the amplifier, setting volume, and cueing the player.
`HomeTheater` is the facade: the caller sends one `watch_movie`
message and the facade plays the whole sequence on the subsystem
objects.

Compare with the procedural Python version, where the caller has to
know — and order — every step:

    projector.on()
    projector.wide_screen()
    amp.on()
    amp.set_volume(5)
    dvd.on()
    dvd.play(title)

POOP hides that choreography behind a single method. The subsystem
still exists for power users; the facade is the easy path.

Smalltalk:
    HomeTheater>>watchMovie: aTitle
        ^{ projector on.
           projector wideScreen.
           amp on.
           amp setVolume: 5.
           dvd on.
           dvd play: aTitle }
"""


class Amplifier:
    def on(self):
        return "amplifier on"

    def set_volume(self, level):
        return "amplifier volume " + level.repr()


class DvdPlayer:
    def on(self):
        return "dvd player on"

    def play(self, title):
        return "playing '" + title + "'"


class Projector:
    def on(self):
        return "projector on"

    def wide_screen(self):
        return "projector in widescreen mode"


class HomeTheater:
    def __init__(self, amplifier, dvd, projector):
        self._amplifier = amplifier
        self._dvd = dvd
        self._projector = projector

    def watch_movie(self, title):
        return [
            self._projector.on(),
            self._projector.wide_screen(),
            self._amplifier.on(),
            self._amplifier.set_volume(5),
            self._dvd.on(),
            self._dvd.play(title),
        ]


theater = HomeTheater(Amplifier(), DvdPlayer(), Projector())
theater.watch_movie("Blade Runner").do(lambda step: step.print())
