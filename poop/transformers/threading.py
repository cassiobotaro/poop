from poop.types.threading import (
    Barrier,
    Event,
    Lock,
    RLock,
    Semaphore,
    Thread,
    Threading,
)

NAMESPACE: dict[str, object] = {
    "threading": Threading,
    "Thread": Thread,
    "Lock": Lock,
    "RLock": RLock,
    "Event": Event,
    "Semaphore": Semaphore,
    "Barrier": Barrier,
}
