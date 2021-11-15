from poop.hfdp.command.simpleremote.garage_door import GarageDoor
from poop.hfdp.command.simpleremote.garage_door_open_command import (
    GarageDoorOpenCommand,
)
from poop.hfdp.command.simpleremote.light import Light
from poop.hfdp.command.simpleremote.light_on_command import LightOnCommand
from poop.hfdp.command.simpleremote.simple_remote_control import (
    SimpleRemoteControl,
)


def main() -> None:
    remote = SimpleRemoteControl()

    light = Light()
    garage_door = GarageDoor()
    light_on_command = LightOnCommand(light)
    garage_open_command = GarageDoorOpenCommand(garage_door)

    remote.set_command(light_on_command)
    remote.button_was_pressed()
    remote.set_command(garage_open_command)
    remote.button_was_pressed()
