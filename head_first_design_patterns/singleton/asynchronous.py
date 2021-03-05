"""
Notes:
    - instances share the same Lock
    - uses lock to prevent running conditions
    - just for fun with async
"""
import asyncio


class SafeSingletonMeta(type):

    _instances = {}
    _lock = asyncio.Lock()

    async def __call__(cls, *args, **kwargs):
        async with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Singleton(metaclass=SafeSingletonMeta):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"I'm a classic Singleton {self.value}"


async def test_multithread(value):
    singleton = await Singleton(value)
    print(singleton.value)


async def main():
    await asyncio.gather(*(test_multithread(value) for value in range(1, 11)))


asyncio.run(main())
