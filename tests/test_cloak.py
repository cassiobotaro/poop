"""No wrapper leaks its internal class name through `__qualname__`.

The cloak covered `__name__` and `__module__`, and CPython prefers
`__qualname__` in several of its own messages — including Python 3.14's
unhashable-key error, which put both spellings in one sentence:

    {[1]: 2}  ->  cannot use 'List' as a dict key (unhashable type: 'list')

Sweeping every class is the point: a per-wrapper assertion says nothing about
the next wrapper, and this leak reached all of them at once.
"""

import importlib
import inspect
import pkgutil

import pytest

import poop.types
from poop import Interpreter
from poop.errors import ExecutionError
from poop.types.meta import PoopMeta


def _classes() -> list[type]:
    """Every POOP class, found through the metaclass every one of them shares.

    `__module__` cannot select them — the cloak sets it to `builtins`, which is
    where the real ones live too — and `inspect.getfile` refuses a class that
    claims to be a builtin. `PoopMeta` is the one mark the cloak does not touch.
    """
    found: dict[int, type] = {}
    for info in pkgutil.iter_modules(poop.types.__path__):
        module = importlib.import_module(f"poop.types.{info.name}")
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if isinstance(cls, PoopMeta):
                found[id(cls)] = cls
    return sorted(found.values(), key=lambda cls: (cls.__name__, id(cls)))


@pytest.mark.parametrize(
    ("index", "cls"),
    list(enumerate(_classes())),
    # Names repeat — Boolean and both singletons all answer `bool` — so the
    # index keeps the ids unique without hiding which class failed.
    ids=lambda arg: arg.__name__ if isinstance(arg, type) else str(arg),
)
def test_qualname_matches_name(index: int, cls: type) -> None:
    assert cls.__qualname__ == cls.__name__


def test_sweep_reaches_the_wrappers() -> None:
    """A collector that stopped finding classes would report a clean run."""
    assert len(_classes()) > 40


def test_unhashable_key_message_names_no_wrapper() -> None:
    """CPython composes this one out of `__qualname__`, so it is the witness."""
    with pytest.raises(ExecutionError, match="cannot use 'list' as a dict key"):
        Interpreter().run_source("d = {[1]: 2}")


def test_unhashable_element_message_names_no_wrapper() -> None:
    with pytest.raises(ExecutionError, match="cannot use 'list' as a set element"):
        Interpreter().run_source("s = {[1]}")
