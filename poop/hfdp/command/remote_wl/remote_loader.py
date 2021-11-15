from poop.hfdp.command.remote_wl.ceiling_fan import CeilingFan
from poop.hfdp.command.remote_wl.garage_door import GarageDoor
from poop.hfdp.command.remote_wl.light import Light
from poop.hfdp.command.remote_wl.remote_control import RemoteControl
from poop.hfdp.command.remote_wl.stereo import Stereo


def main() -> None:
    remote_control = RemoteControl()

    living_room_light = Light("Living Room")
    kitchen_light = Light("Kitchen")
    ceiling_fan = CeilingFan("Living Room")
    garage_door = GarageDoor("Garage")
    stereo = Stereo("Living Room")

    remote_control.set_command(0, living_room_light.on, living_room_light.off)
    remote_control.set_command(1, kitchen_light.on, kitchen_light.off)
    remote_control.set_command(2, ceiling_fan.high, ceiling_fan.off)

    def stereo_on_with_cd() -> None:
        stereo.on()
        stereo.set_cd()
        stereo.set_volume(11)

    remote_control.set_command(3, stereo_on_with_cd, stereo.off)
    remote_control.set_command(4, garage_door.up, garage_door.down)

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
