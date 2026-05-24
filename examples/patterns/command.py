"""
Command — wrap a request as an object you can store, run, and undo

Each action on the `Light` becomes a command object that knows how to
`execute` itself and how to `undo` itself. A `RemoteControl` runs
commands without knowing what they do, keeps a history, and can walk
the last one back — the foundation of every undo stack.

Compare with the procedural Python version:

    if button == "on":
        light.on()
    elif button == "off":
        light.off()
    # ...and now bolt on undo by hand

POOP forbids that dispatch table. The command *is* the request: pass
it around, queue it, log it, reverse it — all by sending messages.

Smalltalk:
    LightOnCommand>>execute ^light on
    LightOnCommand>>undo    ^light off

    RemoteControl>>submit: aCommand
        history addLast: aCommand.
        ^aCommand execute
"""


class Light:
    def on(self):
        return "light on"

    def off(self):
        return "light off"


class LightOnCommand:
    def __init__(self, light):
        self._light = light

    def execute(self):
        return self._light.on()

    def undo(self):
        return self._light.off()


class LightOffCommand:
    def __init__(self, light):
        self._light = light

    def execute(self):
        return self._light.off()

    def undo(self):
        return self._light.on()


class RemoteControl:
    def __init__(self):
        self._history = []

    def submit(self, command):
        self._history.append(command)
        command.execute().print()

    def undo_last(self):
        ("undo: " + self._history.pop().undo()).print()


light = Light()
remote = RemoteControl()

remote.submit(LightOnCommand(light))
remote.submit(LightOffCommand(light))
remote.undo_last()  # reverses the last command: light on again
