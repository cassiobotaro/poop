from typing import Protocol

# ABC is used to formalize an interface.
# Given the dynamic nature of python, this definition would not be necessary,
# every instance of a class that has the quack method could be
# considered a quacking behavior.
# Each class have your own implementation of method quack.
# Program to interface not the implementation.
# Do not confuse with the reserved word interface of some languages.
# The concept here has to do with the way in which
# objects communicate (messages).
# All classes are QuackBehavior due to the quack method.
# No inheritance is needed.
# Structural typing is used here.


class QuackBehavior(Protocol):
    def quack(self):
        ...


class Quack:
    def quack(self):
        print("Quack!")


class Squeak:
    def quack(self):
        print("Squeak!")


class MuteQuack:
    def quack(self):
        print("<< silence >>")


# QuackBehavior is easy to extend.
# Instead of conditional (if) use a class to represent
# negative behaviors (MuteQuack)
