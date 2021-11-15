"""
Notes: - create an application with two buttons and a
label to represent a light - command pattern is used to decouple who executes the command (buttons)
from objects that know how to perform the requests (light) - our commands are called actions and use function instead of a class
"""
"""
Notes: - Command was used here to indicate that the expected type
is a function with no arguments and no return value - Order (line 24) should be a command - Customer can create an order (simplified here for just one order) - Customer take order using waitress instance - Waitress take order without know the order implementation - When you order something, cook is called to make your diner - Note that the kitchen invokes the preparation of the order without
knowing how it will be prepared by the cook
"""
"""
Notes: - Each class represents a piece of equipment. - An equipment will have its methods invoked through commands, so whoever
invokes does not need to know the implementation of the same.
"""
"""
Notes: - Remote Control will be configured with commands
to turn on/off equipaments, but can undo last action - We use MacroCommand (special command who group a lot of commands),
to start/end a party - RemoteControl is decoupled of real equipaments, it invokes commands that
perform this interaction
"""
"""
Notes: - A remote control contains 7 slots for "on" commands,
and 7 for "off" commands - Each command (on or off) is a ReversibleCommand, this means
that the command can be invoked and also have an undo method
to revert your state - NoCommand is used as a Null Object - This example demonstates how we can do reversible commands, and shows
that unfornately we can't simplify using functions (or lambdas)
"""
"""
Notes: - Usage of functions/methods are a convenience rather than defining a lot
of classes - no_command is a way to define a null object - Methods can be used as commands because they are also callable,
they are functions linked to data structure (classes) - Decouple object making a request(RemoteControl)
from the one that knows how to peform it (equipament)
"""
"""
Notes: - Undoable is an interface that defines what "undoable"
should implement the undo method - Callable is an interface that defines what "callable"
should implement the **call** method - ReversibleCommand combines both interfaces - MacroCommand is just a ReversibleCommand Agreggator,
it will consist of several commands that will be executed together - NoCommand is a null object command 9do nothing) - Commands will be used to decouple the invocator of a command from
the objects that will actually perform the task.
"""
""" - RemoteControl is a simple remote control with one slot to store a command - Command should be a callable (contians method **call**) - we can change command using it's interface - The purpose here is to demonstrate that when an action of the remote
control occurs, there is an interaction with the equipment without the
executor of the action (the one who controls the remote control) knowing
the concrete implementation of the executed command.
"""
