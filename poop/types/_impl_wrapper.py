"""Mixin for POOP types that wrap a CPython object as `self._impl`.

Many `poop/types/<module>.py` classes wrap an existing CPython object
(`datetime.datetime`, `ipaddress.IPv4Address`, `threading.Thread`, …)
by storing it as `self._impl`. When a stdlib API hands back an
already-constructed Python object — e.g. `threading.current_thread()`
returns a `Thread` we didn't make — the wrapper bypasses `__init__`
and assigns `_impl` directly:

    obj = Wrapper.__new__(Wrapper)
    obj._impl = py_obj
    return obj

This mixin makes the bypass explicit: every wrapper gains a uniform
`Wrapper._from_impl(py_obj)` classmethod.
"""

from __future__ import annotations

from typing import Any, Self


class _ImplWrapperMixin:
    """Adds `_from_impl(cls, impl)` to any wrapper that stores `self._impl`."""

    __slots__ = ()

    @classmethod
    def _from_impl(cls, impl: Any) -> Self:
        obj = cls.__new__(cls)
        obj._impl = impl
        return obj
