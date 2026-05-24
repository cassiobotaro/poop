"""
Memento — capture an object's state so it can be restored later

An `Editor` can hand out a `Snapshot` of its contents and later accept
one back to undo changes. The snapshot is opaque: only the editor
reads its state. A `History` caretaker stacks snapshots without ever
inspecting them, giving you undo without breaking encapsulation.

Compare with the procedural Python version, which reaches in and
copies the editor's private field directly:

    saved = editor._content          # poking at internals
    editor._content = "..."          # mutate
    editor._content = saved          # restore

POOP keeps the state behind messages. The editor decides what to put
in a snapshot and how to read one back; the caretaker just holds them.

Smalltalk:
    Editor>>save           ^Snapshot state: content
    Editor>>restore: aSnapshot
        content := aSnapshot state. ^self

    History>>push: aSnapshot snapshots addLast: aSnapshot
    History>>pop           ^snapshots removeLast
"""


class Snapshot:
    def __init__(self, state):
        self._state = state

    def state(self):
        return self._state


class Editor:
    def __init__(self):
        self._content = ""

    def write(self, text):
        self._content = self._content + text
        return self

    def content(self):
        return self._content

    def save(self):
        return Snapshot(self._content)

    def restore(self, snapshot):
        self._content = snapshot.state()
        return self


class History:
    def __init__(self):
        self._snapshots = []

    def push(self, snapshot):
        self._snapshots.append(snapshot)

    def pop(self):
        return self._snapshots.pop()


editor = Editor()
history = History()

editor.write("Hello")
history.push(editor.save())  # checkpoint

editor.write(", World")
editor.content().print()  # Hello, World

editor.restore(history.pop())  # roll back to the checkpoint
editor.content().print()  # Hello
