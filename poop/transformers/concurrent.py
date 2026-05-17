from poop.types.concurrent import (
    CFFuture,
    Concurrent,
    ProcessPoolExecutor,
    ThreadPoolExecutor,
)

NAMESPACE: dict[str, object] = {
    "concurrent": Concurrent,
    "ThreadPoolExecutor": ThreadPoolExecutor,
    "ProcessPoolExecutor": ProcessPoolExecutor,
    "CFFuture": CFFuture,
}
