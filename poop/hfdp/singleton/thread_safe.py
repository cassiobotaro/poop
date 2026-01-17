"""
Notes:
    - instances share the same Lock
    - uses lock to prevent running conditions
"""

from threading import Lock, Thread


class SafeSingletonMeta(type):

    _instances: dict[type["Singleton"], "Singleton"] = {}
    _lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Singleton(metaclass=SafeSingletonMeta):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"I'm a classic Singleton {self.value}"


def test_singleton(value):
    singleton = Singleton(value)
    print(singleton.value)


process1 = Thread(target=test_singleton, args=("FOO",))
process2 = Thread(target=test_singleton, args=("BAR",))
process1.start()
process2.start()
