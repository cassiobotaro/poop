from poop.types.threading import (
    Barrier,
    BoundedSemaphore,
    Condition,
    Event,
    Lock,
    RLock,
    Semaphore,
    Thread,
    Threading,
    _Local,
)

NAMESPACE: dict[str, object] = {
    "threading": Threading,
    "Thread": Thread,
    "Lock": Lock,
    "RLock": RLock,
    "Event": Event,
    "Semaphore": Semaphore,
    "BoundedSemaphore": BoundedSemaphore,
    "Condition": Condition,
    # `Timer` would collide with timeit.Timer; access via `threading.Timer`.
    "Local": _Local,
    "Barrier": Barrier,
}
