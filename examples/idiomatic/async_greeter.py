"""
Async greeter — sequences two coroutines and prints the combined result.

Smalltalk:
    | hello world |
    hello := [Processor activeProcess sleep: 50. 'Hello'] newProcess.
    world := [Processor activeProcess sleep: 50. 'World'] newProcess.
    hello resume. world resume.
    Transcript showCr: hello value , ' ' , world value.
"""


class Greeter:
    async def slow(self, word, delay):
        await asyncio.sleep(delay)
        return word

    async def run(self):
        hello = await self.slow("Hello", 0.05)
        world = await self.slow("World", 0.01)
        return hello + " " + world


asyncio.run(Greeter().run()).print()
