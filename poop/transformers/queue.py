from poop.types.queue import (
    LifoQueue,
    PriorityQueue,
    Queue,
    QueueNamespace,
    SimpleQueue,
)

NAMESPACE: dict[str, object] = {
    "queue": QueueNamespace,
    "Queue": Queue,
    "LifoQueue": LifoQueue,
    "PriorityQueue": PriorityQueue,
    "SimpleQueue": SimpleQueue,
}
