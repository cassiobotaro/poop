from __future__ import annotations

import graphlib as _graphlib
from typing import Any, ClassVar, cast

from poop.types.boolean import Boolean, false, true
from poop.types.dict import Dict
from poop.types.none import NoneClass, none
from poop.types.tuple import Tuple


def _unwrap_graph(graph: Dict | None) -> dict[Any, list[Any]] | None:
    if graph is None:
        return None
    out: dict[Any, list[Any]] = {}
    for node, preds in graph._data.items():
        # Predecessor collection is typed Object; cast to Any since
        # it's expected to be iterable at runtime.
        out[node] = list(cast(Any, preds))
    return out


class TopologicalSorter:
    """Wraps Python's `graphlib.TopologicalSorter` for topo-sorting
    POOP node graphs.

    Two construction shapes mirror CPython:
    - `TopologicalSorter()` — empty; add edges incrementally with
      `.add(node, *predecessors)`.
    - `TopologicalSorter(graph)` — `graph` is a POOP `Dict[node,
      Iterable[predecessors]]`.
    """

    __slots__ = ("_impl",)

    def __init__(self, graph: Dict | None = None) -> None:
        self._impl = _graphlib.TopologicalSorter(_unwrap_graph(graph))

    def add(self, node: Any, *predecessors: Any) -> NoneClass:
        self._impl.add(node, *predecessors)
        return none

    def prepare(self) -> NoneClass:
        self._impl.prepare()
        return none

    def is_active(self) -> Boolean:
        return true if self._impl.is_active() else false

    def get_ready(self) -> Tuple:
        return Tuple(*self._impl.get_ready())

    def done(self, *nodes: Any) -> NoneClass:
        self._impl.done(*nodes)
        return none

    def static_order(self) -> Tuple:
        return Tuple(*self._impl.static_order())


class Graphlib:
    """Namespace mirroring Python's `graphlib` module.

    `CycleError` is exposed as a raw Python exception class so user
    code can pass it to `Try.except_(...)`.
    """

    CycleError: ClassVar[type[Exception]] = _graphlib.CycleError
    TopologicalSorter: ClassVar[type[TopologicalSorter]] = TopologicalSorter
