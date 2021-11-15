from poop.hfdp.command.remote.ceiling_fan import CeilingFan
from poop.hfdp.command.remote.ceiling_fan_off_command import (
    CeilingFanOffCommand,
)
from poop.hfdp.command.remote.ceiling_fan_on_command import CeilingFanOnCommand
from poop.hfdp.command.remote.garage_door import GarageDoor
from poop.hfdp.command.remote.garage_door_down_command import (
    GarageDoorDownCommand,
)
from poop.hfdp.command.remote.garage_door_up_command import GarageDoorUpCommand
from poop.hfdp.command.remote.light import Light
from poop.hfdp.command.remote.light_off_command import LightOffCommand
from poop.hfdp.command.remote.light_on_command import LightOnCommand
from poop.hfdp.command.remote.remote_control import RemoteControl
from poop.hfdp.command.remote.stereo import Stereo
from poop.hfdp.command.remote.stereo_off_command import StereoOffCommand
from poop.hfdp.command.remote.stereo_on_with_cd_command import (
    StereoOnWithCDCommand,
)


def main() -> None:
    remote_control = RemoteControl()

    living_room_light = Light("Living Room")
    kitchen_light = Light("Kitchen")
    ceiling_fan = CeilingFan("Living Room")
    garage_door = GarageDoor("Garage")
    stereo = Stereo("Living Room")

    living_room_light_on = LightOnCommand(living_room_light)
    living_room_light_off = LightOffCommand(living_room_light)
    kitchen_light_on = LightOnCommand(kitchen_light)
    kitchen_light_off = LightOffCommand(kitchen_light)

    ceiling_fan_on = CeilingFanOnCommand(ceiling_fan)
    ceiling_fan_off = CeilingFanOffCommand(ceiling_fan)

    garage_door_up = GarageDoorUpCommand(garage_door)
    garage_door_down = GarageDoorDownCommand(garage_door)

    stereo_on_with_cd = StereoOnWithCDCommand(stereo)
    stereo_off = StereoOffCommand(stereo)

    remote_control.set_command(0, living_room_light_on, living_room_light_off)
    remote_control.set_command(1, kitchen_light_on, kitchen_light_off)
    remote_control.set_command(2, ceiling_fan_on, ceiling_fan_off)
    remote_control.set_command(3, stereo_on_with_cd, stereo_off)
    remote_control.set_command(4, garage_door_up, garage_door_down)

    print(remote_control)

    remote_control.on_button_was_pushed(0)
    remote_control.off_button_was_pushed(0)
    remote_control.on_button_was_pushed(1)
    remote_control.off_button_was_pushed(1)
    remote_control.on_button_was_pushed(2)
    remote_control.off_button_was_pushed(2)
    remote_control.on_button_was_pushed(3)
    remote_control.off_button_was_pushed(3)
    remote_control.on_button_was_pushed(4)
    remote_control.off_button_was_pushed(4)
