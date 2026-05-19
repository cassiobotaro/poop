"""
Door state machine — polymorphism replacing `if state == ...`

Three states (ClosedDoor, OpenDoor, LockedDoor) each respond to
open/close/lock/unlock. The transition itself is dispatched: the
current state knows what its next state is and returns it. Invalid
transitions raise via `ValueError.raise_(...)` so the caller catches
with `Try`.

Compare with the procedural Python version:

    def transition(state, action):
        if state == "closed" and action == "open":
            return "open"
        elif state == "open" and action == "close":
            return "closed"
        elif state == "closed" and action == "lock":
            return "locked"
        ...

POOP forbids that table. Each state owns its outgoing edges and the
"current state" variable is the state object itself.

Smalltalk:
    ClosedDoor>>open ^OpenDoor new
    ClosedDoor>>close ^self
    ClosedDoor>>lock ^LockedDoor new
    ClosedDoor>>unlock ^self

    OpenDoor>>open ^self
    OpenDoor>>close ^ClosedDoor new
    OpenDoor>>lock ^Error signal: 'cannot lock an open door'
    OpenDoor>>unlock ^self

    LockedDoor>>open ^Error signal: 'door is locked'
    LockedDoor>>close ^self
    LockedDoor>>lock ^self
    LockedDoor>>unlock ^ClosedDoor new
"""


class ClosedDoor:
    def describe(self):
        return "closed"

    def open(self):
        return OpenDoor()

    def close(self):
        return self

    def lock(self):
        return LockedDoor()

    def unlock(self):
        return self


class OpenDoor:
    def describe(self):
        return "open"

    def open(self):
        return self

    def close(self):
        return ClosedDoor()

    def lock(self):
        ValueError.raise_("cannot lock an open door")

    def unlock(self):
        return self


class LockedDoor:
    def describe(self):
        return "locked"

    def open(self):
        ValueError.raise_("door is locked")

    def close(self):
        return self

    def lock(self):
        return self

    def unlock(self):
        return ClosedDoor()


door = ClosedDoor()
door.describe().print()
door = door.open()
door.describe().print()
door = door.close().lock()
door.describe().print()

Try(lambda: door.open()).except_(
    ValueError,
    lambda e: ("refused: " + e.message()).print(),
).run()

door = door.unlock().open()
door.describe().print()
