from __future__ import annotations

import queue as _queue
from typing import Any, ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object


def _opt_timeout(timeout: Float | Int | None) -> Any:
    if timeout is None:
        return None
    return timeout._value


class _BaseQueue(Object):
    """Common shape for FIFO / LIFO / Priority / SimpleQueue."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    def put(
        self,
        item: Any,
        block: Boolean | None = None,
        timeout: Float | Int | None = None,
    ) -> NoneClass:
        b = True if block is None else bool(block)
        self._impl.put(item, b, _opt_timeout(timeout))
        return none

    def put_nowait(self, item: Any) -> NoneClass:
        self._impl.put_nowait(item)
        return none

    def get(
        self,
        block: Boolean | None = None,
        timeout: Float | Int | None = None,
    ) -> Any:
        b = True if block is None else bool(block)
        return self._impl.get(b, _opt_timeout(timeout))

    def get_nowait(self) -> Any:
        return self._impl.get_nowait()

    def qsize(self) -> Int:
        return Int(self._impl.qsize())

    def empty(self) -> Boolean:
        return true if self._impl.empty() else false

    def full(self) -> Boolean:
        return true if self._impl.full() else false


class Queue(_BaseQueue):
    """Wraps `queue.Queue` — FIFO queue with task tracking."""

    def __init__(self, maxsize: Int | None = None) -> None:
        m = 0 if maxsize is None else maxsize._value
        super().__init__(_queue.Queue(m))

    def task_done(self) -> NoneClass:
        self._impl.task_done()
        return none

    def join(self) -> NoneClass:
        self._impl.join()
        return none


class LifoQueue(_BaseQueue):
    """Wraps `queue.LifoQueue` — LIFO (stack) queue."""

    def __init__(self, maxsize: Int | None = None) -> None:
        m = 0 if maxsize is None else maxsize._value
        super().__init__(_queue.LifoQueue(m))

    def task_done(self) -> NoneClass:
        self._impl.task_done()
        return none

    def join(self) -> NoneClass:
        self._impl.join()
        return none


class PriorityQueue(_BaseQueue):
    """Wraps `queue.PriorityQueue` — heap-based priority queue."""

    def __init__(self, maxsize: Int | None = None) -> None:
        m = 0 if maxsize is None else maxsize._value
        super().__init__(_queue.PriorityQueue(m))

    def task_done(self) -> NoneClass:
        self._impl.task_done()
        return none

    def join(self) -> NoneClass:
        self._impl.join()
        return none


class SimpleQueue(Object):
    """Wraps `queue.SimpleQueue` — lightweight FIFO without task tracking."""

    __slots__ = ("_impl",)

    def __init__(self) -> None:
        self._impl = _queue.SimpleQueue()

    def put(self, item: Any) -> NoneClass:
        self._impl.put(item)
        return none

    def put_nowait(self, item: Any) -> NoneClass:
        self._impl.put_nowait(item)
        return none

    def get(
        self,
        block: Boolean | None = None,
        timeout: Float | Int | None = None,
    ) -> Any:
        b = True if block is None else bool(block)
        return self._impl.get(b, _opt_timeout(timeout))

    def get_nowait(self) -> Any:
        return self._impl.get_nowait()

    def qsize(self) -> Int:
        return Int(self._impl.qsize())

    def empty(self) -> Boolean:
        return true if self._impl.empty() else false


class QueueNamespace:
    """Namespace mirroring Python's `queue` module."""

    Queue: ClassVar[type[Queue]] = Queue
    LifoQueue: ClassVar[type[LifoQueue]] = LifoQueue
    PriorityQueue: ClassVar[type[PriorityQueue]] = PriorityQueue
    SimpleQueue: ClassVar[type[SimpleQueue]] = SimpleQueue

    # Errors
    Empty: ClassVar[type[BaseException]] = _queue.Empty
    Full: ClassVar[type[BaseException]] = _queue.Full
