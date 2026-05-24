"""
Mediator — colleagues talk through a hub instead of to each other

In a chat room, no `User` holds a reference to any other user. They
all know one `ChatRoom`, the mediator: a user `send`s to the room and
the room `broadcast`s to everyone else. Add or remove a participant
and no other participant has to change.

Compare with the procedural Python version, where each user keeps a
list of peers and loops over them:

    for peer in self.peers:
        if peer is not self:
            peer.receive(self.name, message)

POOP forbids the `for` and the `is`. Routing lives in one place — the
mediator — so the colleagues stay simple and decoupled.

Smalltalk:
    ChatRoom>>broadcast: message from: sender
        users do: [:u | u deliverFrom: sender message: message]

    User>>deliverFrom: sender message: message
        sender = name ifFalse: [
            Transcript showCr: name , ' <- ' , sender , ': ' , message]
"""


class ChatRoom:
    def __init__(self):
        self._users = []

    def register(self, user):
        self._users.append(user)

    def broadcast(self, sender, message):
        self._users.do(lambda user: user.deliver(sender, message))


class User:
    def __init__(self, name, room):
        self._name = name
        self._room = room
        room.register(self)

    def send(self, message):
        self._room.broadcast(self._name, message)

    def deliver(self, sender, message):
        (sender == self._name).if_false(
            lambda: (self._name + " <- " + sender + ": " + message).print()
        )


room = ChatRoom()
alice = User("Alice", room)
bob = User("Bob", room)
User("Carol", room)

alice.send("hi everyone")
bob.send("hey Alice")
