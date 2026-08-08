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


# --- the same leak one frame in: the *function's* qualname ---
#
# CPython builds a call-signature error out of `__qualname__` on the function,
# frozen when the class body ran and untouched by the class-level cloak. So
# every wrong-arity message in the language answered in POOP's internal
# vocabulary — `Str.upper()`, `List.append()`, `Dict.__init__()` — and a method
# reached through a mixin leaked a *private* name, `_IterableMixin.map()`,
# which is exactly what `_reject_private` refuses to hand out.


def _own_functions(cls: type) -> list[tuple[str, object]]:
    return [(name, getattr(attr, "__func__", attr)) for name, attr in vars(cls).items()]


@pytest.mark.parametrize(
    ("index", "cls"),
    list(enumerate(_classes())),
    ids=lambda arg: arg.__name__ if isinstance(arg, type) else str(arg),
)
def test_own_functions_answer_the_cloaked_class_name(index: int, cls: type) -> None:
    # The owner half only. An alias (`__repr__ = __str__`) binds one function
    # under two names, and the cloak renames it after the function's own
    # `__name__` — the binding it is defined as, which is the one CPython
    # reports. What must never differ is the class part.
    for _, fn in _own_functions(cls):
        if inspect.isfunction(fn):
            assert fn.__qualname__.startswith(f"{cls.__qualname__}.")


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ('"abc".upper(1)', "str.upper()"),
        ("[1].append()", "list.append()"),
        ('{"a": 1}.at()', "dict.at()"),
        ("{1}.add()", "set.add()"),
        ("(1).round(1, 2)", "int.round()"),
        ("dict(1, 2, 3)", "dict.__init__()"),
        # Inherited from a mixin, which owns no builtin name of its own: cloaked
        # as `object`, the root's spelling, rather than as a private one.
        ("[1, 2].map()", "object.map()"),
        ("[1].iter().next(1, 2)", "object.next()"),
        ('{"a": 1}.keys().len(1)', "object.len()"),
        # The rewriter helpers, whose mangled key `no_poop_prefix` reserves —
        # so the message named a spelling the interpreter would then refuse.
        ("range(1, 2, 3, 4)", "range()"),
        ("int(1, 2, 3)", "int()"),
        ("float(1, 2)", "float()"),
        ("bool(1, 2)", "bool()"),
        ("enumerate([1], 2, 3)", "enumerate()"),
    ],
)
def test_arity_errors_name_no_internal_spelling(source: str, expected: str) -> None:
    with pytest.raises(ExecutionError) as caught:
        Interpreter().run_source(source)
    message = str(caught.value)
    assert expected in message
    assert "_poop_" not in message


def test_namespace_helpers_carry_no_reserved_prefix() -> None:
    """The sweep behind the table above: every binding, not the sampled ones."""
    from poop.transformers import DEFAULT_NAMESPACE

    for key, value in DEFAULT_NAMESPACE.items():
        if inspect.isfunction(value):
            assert not value.__qualname__.startswith("_poop_"), key
            assert "<locals>" not in value.__qualname__, key
