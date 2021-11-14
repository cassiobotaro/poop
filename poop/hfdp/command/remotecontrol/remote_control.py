"""
Notes:
    - Usage of functions/methods are a convenience rather than defining a lot
    of classes
    - no_command is a way to define a null object
    - Methods can be used as commands because they are also callable,
    they are functions linked to data structure (classes)
    - Decouple object making a request(RemoteControl)
    from the one that knows how to peform it (equipament)
"""
from equipament import CeilingFan, GarageDoor, Light, Stereo


class RemoteControl:
    def __init__(self):
        def no_command():
            ...

        self._on_commands = [no_command for _ in range(7)]
        self._off_commands = [no_command for _ in range(7)]

    def set_command(self, slot, on_command, off_command):
        self._on_commands[slot] = on_command
        self._off_commands[slot] = off_command

    def on_button_was_pushed(self, slot):
        command = self._on_commands[slot]
        command()

    def off_button_was_pushed(self, slot):
        command = self._off_commands[slot]
        command()

    def __str__(self) -> str:
        title = "\n------ Remote Control ------\n"
        commands = "\n".join(
            f"[slot {index}] {self._on_commands[index].__qualname__} "
            f"{self._off_commands[index].__qualname__}"
            for index in range(7)
        )
        return f"{title}\n{commands}\n"


if __name__ == "__main__":
    remote_control = RemoteControl()

    living_room_light = Light("Living Room")
    kitchen_light = Light("Kitchen")
    ceiling_fan = CeilingFan("Living Room")
    garage_door = GarageDoor("Main House")
    stereo = Stereo("Living Room")

    remote_control.set_command(0, living_room_light.on, living_room_light.off)
    remote_control.set_command(1, kitchen_light.on, kitchen_light.off)
    remote_control.set_command(2, ceiling_fan.high, ceiling_fan.off)

    def stereo_with_CD():
        stereo.on()
        stereo.set_cd()
        stereo.set_volume(11)

    remote_control.set_command(3, stereo_with_CD, stereo.off)
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
    remote_control.on_button_was_pushed(5)
    remote_control.off_button_was_pushed(5)
