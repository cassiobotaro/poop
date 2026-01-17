from typing import Protocol

# Each class have your own implementation of method quack.
# Program to interface not the implementation.
# Do not confuse with the reserved word interface of some languages.
# The concept here has to do with the way in which
# objects communicate (messages).
# All classes are FlyBehavior due to the fly method. No inheritance is needed.
# Structural typing is used here.


class FlyBehavior(Protocol):
    def fly(self): ...


class FlyWithWings:
    def fly(self):
        print("I'm flying")


class FlyNoWay:
    def fly(self):
        print("I can't fly")


class FlyRocketPowered:
    def fly(self):
        print("I'm flying with a rocket")


# FlyBehavior is easy to extend.
# Instead of conditional (if) use a class to represent
# negative behaviors (FlyNoWay)
