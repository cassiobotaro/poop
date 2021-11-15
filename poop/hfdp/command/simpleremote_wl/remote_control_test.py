from poop.hfdp.command.simpleremote_wl.garage_door import GarageDoor
from poop.hfdp.command.simpleremote_wl.light import Light
from poop.hfdp.command.simpleremote_wl.simple_remote_control import (
    SimpleRemoteControl,
)


def main() -> None:
    remote = SimpleRemoteControl()

    light = Light()
    garage_door = GarageDoor()

    remote.set_command(light.on)
    remote.button_was_pressed()
    remote.set_command(garage_door.up)
    remote.button_was_pressed()
    remote.set_command(garage_door.light_on)
    remote.button_was_pressed()
    remote.set_command(garage_door.light_off)
    remote.button_was_pressed()
