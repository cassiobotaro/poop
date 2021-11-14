from poop.hfdp.command.party.command import Command
from poop.hfdp.command.party.hottub import Hottub
from poop.hfdp.command.party.hottub_off_command import HottubOffCommand
from poop.hfdp.command.party.hottub_on_command import HottubOnCommand
from poop.hfdp.command.party.light import Light
from poop.hfdp.command.party.light_off_command import LightOffCommand
from poop.hfdp.command.party.light_on_command import LightOnCommand
from poop.hfdp.command.party.macro_command import MacroCommand
from poop.hfdp.command.party.remote_control import RemoteControl
from poop.hfdp.command.party.stereo import Stereo
from poop.hfdp.command.party.stereo_off_command import StereoOffCommand
from poop.hfdp.command.party.stereo_on_command import StereoOnCommand
from poop.hfdp.command.party.tv import TV
from poop.hfdp.command.party.tv_off_command import TVOffCommand
from poop.hfdp.command.party.tv_on_command import TVOnCommand


def main():
    remote_control = RemoteControl()

    light = Light("Living Room")
    tv = TV("Living Room")
    stereo = Stereo("Living Room")
    hottub = Hottub()

    light_on = LightOnCommand(light)
    stereo_on = StereoOnCommand(stereo)
    tv_on = TVOnCommand(tv)
    hottub_on = HottubOnCommand(hottub)
    light_off = LightOffCommand(light)
    stereo_off = StereoOffCommand(stereo)
    tv_off = TVOffCommand(tv)
    hottub_off = HottubOffCommand(hottub)

    party_on: list[Command] = [light_on, stereo_on, tv_on, hottub_on]
    party_off: list[Command] = [light_off, stereo_off, tv_off, hottub_off]

    party_on_macro = MacroCommand(party_on)
    party_off_macro = MacroCommand(party_off)

    remote_control.set_command(0, party_on_macro, party_off_macro)

    print(remote_control)
    print("\n--- Pushing Macro On---\n")
    remote_control.on_button_was_pushed(0)
    print("\n--- Pushing Macro Off---\n")
    remote_control.off_button_was_pushed(0)
