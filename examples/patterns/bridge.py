"""
Bridge — vary an abstraction and its implementation independently

A `Remote` is the abstraction; a `Device` (TV or Radio) is the
implementation. The remote holds a device and talks to it through a
small interface, so the two hierarchies grow on their own axes: add an
`AdvancedRemote` without touching any device, add a `Speaker` without
touching any remote.

Compare with the procedural Python version, where every pairing is a
class — `TVRemote`, `RadioRemote`, `AdvancedTVRemote`, ... — and the
count explodes:

    class AdvancedTVRemote: ...
    class AdvancedRadioRemote: ...

POOP keeps the two sides apart and bridges them by holding a
reference. Remotes × Devices combine at runtime, not in the class
list.

Smalltalk:
    Remote>>volumeUp
        volume := volume + 10.
        ^device setVolume: volume

    AdvancedRemote>>mute
        ^device setVolume: 0
"""


# Implementation hierarchy — devices.
class TV:
    def set_volume(self, percent):
        return "TV volume now " + percent.repr()


class Radio:
    def set_volume(self, percent):
        return "Radio volume now " + percent.repr()


# Abstraction hierarchy — remotes, each holding a device.
class Remote:
    def __init__(self, device):
        self._device = device
        self._volume = 0

    def volume_up(self):
        self._volume = self._volume + 10
        return self._device.set_volume(self._volume)


class AdvancedRemote(Remote):
    def mute(self):
        self._volume = 0
        return self._device.set_volume(0)


Remote(TV()).volume_up().print()
Remote(Radio()).volume_up().print()

advanced = AdvancedRemote(TV())
advanced.volume_up().print()
advanced.mute().print()
