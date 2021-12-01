import typing

if typing.TYPE_CHECKING:
    from poop.hfdp.facade.home_theater.amplifier import Amplifier


class Tuner:
    def __init__(self, description: str, amp: "Amplifier") -> None:
        self._description = description
        self._amplifier: "Amplifier" = amp
        self._frequency: float = 0.0

    def on(self) -> None:
        print(self._description + " on")

    def off(self) -> None:
        print(self._description + " off")

    def set_frequency(self, frequency: float) -> None:
        print(f"{self._description} setting frequency to {frequency}")
        self._frequency = frequency

    def set_am(self) -> None:
        print(f"{self._description} setting AM mode")

    def set_fm(self) -> None:
        print(f"{self._description} setting FM mode")

    def __str__(self) -> str:
        return self._description
