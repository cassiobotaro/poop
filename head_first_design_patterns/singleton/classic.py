"""
Notes:
    - python don't have private constructors
    - can be implemented using base class, decorator, metaclass
    - use of the __call__ method, thus avoiding being overwritten
    with inheritance
    - __new__ (constructor?) could also be used
    - i could have used only one instance (default None),
    instead of a dictionary (_instancies) in the implementation,
    but this would imply a problem with inheritance / metaclass
    - funny: you can instantiate a class, then delete it
    Now you have the unique instance of that class
"""


class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    def __str__(self):
        return "I'm a classic Singleton"


class OtherSingleton(metaclass=SingletonMeta):
    def __str__(self):
        return "I'm other Singleton"


if __name__ == "__main__":
    s1 = Singleton()
    s2 = Singleton()
    s3 = OtherSingleton()
    print(f"{s1}")
    print(f"{s2}")
    print(f"{s3}")
    print(f"{id(s1)=}")
    print(f"{id(s2)=}")
    print(f"{id(s3)=}")
