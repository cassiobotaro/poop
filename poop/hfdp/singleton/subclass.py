"""
Notes:
    - implementation allow inheritance
    - each subclass have your own unique instance
"""

from classic import Singleton


class CoolerSingleton(Singleton):
    pass


class HotterSingleton(Singleton):
    pass


if __name__ == "__main__":
    foo = CoolerSingleton()
    spam = CoolerSingleton()
    bar = HotterSingleton()
    print(f"{foo=} is not {bar=}")
    print(f"{foo=} is {spam=}")
