from poop.types.multiprocessing import MPQueue, Multiprocessing, Pool

NAMESPACE: dict[str, object] = {
    "multiprocessing": Multiprocessing,
    # `Process` collides with the `os.process` namespace, so the
    # multiprocessing.Process is reachable as `multiprocessing.Process`.
    "Pool": Pool,
    "MPQueue": MPQueue,
}
