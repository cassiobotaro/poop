"""
Decorator pattern — composition by delegation

A base `Greeter` is wrapped by `LoggedGreeter` (acts before the call)
and `ShoutingGreeter` (acts after). Each wrapper holds an inner
greeter and forwards `greet(name)` to it, layering its own behavior.
Stack as many as you want — same message, longer chain.

Compare with the procedural Python version, where every combination
needs its own branch:

    if logged and shouting:
        ...
    elif logged:
        ...
    elif shouting:
        ...
    else:
        ...

POOP forbids that table. Wrappers compose by nested constructors,
and the greeted object never knows how deep the stack is.

Smalltalk:
    Greeter>>greet: name
        ^'Hello, ', name

    LoggedGreeter>>greet: name
        Transcript show: '[log] greeting ', name; cr.
        ^inner greet: name

    ShoutingGreeter>>greet: name
        ^(inner greet: name) asUppercase
"""


class Greeter:
    def greet(self, name):
        return "Hello, " + name


class LoggedGreeter:
    def __init__(self, inner):
        self._inner = inner

    def greet(self, name):
        ("[log] greeting " + name).print()
        return self._inner.greet(name)


class ShoutingGreeter:
    def __init__(self, inner):
        self._inner = inner

    def greet(self, name):
        return self._inner.greet(name).upper()


# Plain greeter
Greeter().greet("Alice").print()

# Wrap with logging
LoggedGreeter(Greeter()).greet("Bob").print()

# Stack: shout(log(greet))
ShoutingGreeter(LoggedGreeter(Greeter())).greet("Carol").print()
