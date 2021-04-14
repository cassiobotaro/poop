from enum import Enum


class GarageDoor:
    def __init__(self, location):
        self.__location = location

    def up(self):
        print(f"{self.__location} garage door is up")

    def down(self):
        print(f"{self.__location} garage door is up")

    def light_on(self):
        print(f"{self.__location} garage light is on")

    def light_off(self):
        print(f"{self.__location} garage light is off")


class CeilingFan:
    SPEED = Enum("SPEED", "HIGH MEDIUM LOW OFF")
    speed = SPEED.OFF

    def __init__(self, location):
        self.__location = location

    def high(self):
        self.speed = self.SPEED.HIGH
        print(f"{self.__location} ceiling fan is on high")

    def medium(self):
        self.speed = self.SPEED.MEDIUM
        print(f"{self.__location} ceiling fan is on medium")

    def low(self):
        self.speed = self.SPEED.LOW
        print(f"{self.__location} ceiling fan is on low")

    def off(self):
        self.speed = self.SPEED.OFF
        print(f"{self.__location} ceiling fan is off")

    def get_speed(self):
        return self.speed


class Hottub:
    INITIAL_TEMP = 0

    def __init__(self):
        self.__temperature = self.INITIAL_TEMP
        self.__on = False

    def on(self):
        self.__on = True

    def off(self):
        self.__off = False

    def circulate(self):
        if self.__on:
            print("Hottub is bubbling")

    def jets_on(self):
        print("Hottub jets are on")

    def jets_off(self):
        print("Hottub jets are off")

    def set_temperature(self, temperature: int):
        if temperature > self.__temperature:
            print(f"Hottub is heating to a steaming {temperature} degrees")
        else:
            print(f"Hottub is cooling to {temperature} degrees")


class Light:
    OFF_LEVEL = 0
    ON_LEVEL = 0

    def __init__(self, location):
        self.__level = self.OFF_LEVEL
        self.__location = location

    def on(self):
        self.__level = self.ON_LEVEL
        print(f"{self.__location} light is on")

    def off(self):
        self.__level = self.OFF_LEVEL
        print(f"{self.__location} light is off")

    def dim(self, level):
        self.__level = level
        if level == self.OFF_LEVEL:
            self.off()
        else:
            print("Light is dimmed to {self.__level}%")

    def get_level(self):
        return self.__level


class Stereo:
    TURNED_OFF = 0

    def __init__(self, location):
        self.__location = location
        self.__volume = self.TURNED_OFF

    def on(self):
        print(f"{self.__location} stereo is on")

    def off(self):
        print(f"{self.__location} stereo is off")

    def set_cd(self):
        print(f"{self.__location} is set for CD input")

    def set_dvd(self):
        print(f"{self.__location} is set for DVD input")

    def set_radio(self):
        print(f"{self.__location} is set for Radio")

    def set_volume(self, volume: int):
        if 1 < volume < 11:
            self.__volume = volume
            print(f"{self.__location} Stereo volume set to {volume}")


class TV:
    INITIAL_CHANNEL = 0
    DVD_CHANNEL = 3

    def __init__(self, location: str):
        self.__location = location
        self.__channel = self.INITIAL_CHANNEL

    def on(self):
        print(f"{self.__location} TV is on")

    def off(self):
        print(f"{self.__location} TV is off")

    def set_input_channel(self):
        self.__channel = self.DVD_CHANNEL
        print(f"{self.__location} TV is set for DVD")
