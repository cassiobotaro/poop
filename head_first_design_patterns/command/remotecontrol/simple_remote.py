from equipament import GarageDoor


class RemoteControl:
    def __init__(self):
        def no_command():
            ...

        self.__slot = no_command

    def set_command(self, command):
        self.__slot = command

    def button_was_pressed(self):
        self.__slot()


if __name__ == "__main__":
    simple_remote_control = RemoteControl()

    garage_door = GarageDoor("Main House")

    simple_remote_control.set_command(garage_door.light_on)
    simple_remote_control.button_was_pressed()
    simple_remote_control.set_command(garage_door.up)
    simple_remote_control.button_was_pressed()
    simple_remote_control.set_command(garage_door.light_off)
    simple_remote_control.button_was_pressed()
    simple_remote_control.set_command(garage_door.down)
    simple_remote_control.button_was_pressed()
