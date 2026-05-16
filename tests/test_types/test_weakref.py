import gc

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.weakref import (
    WeakKeyDictionary,
    WeakRef,
    Weakref,
    WeakSet,
    WeakValueDictionary,
)

# gc.collect() inside these tests reclaims unrelated objects (e.g. orphan
# sqlite3 Connections from other test modules), surfacing their cleanup
# warnings here. Silence them — they're not weakref behavior.
pytestmark = pytest.mark.filterwarnings("ignore::ResourceWarning")


class _UserClass(Object):
    """A POOP user-style class (no __slots__, so it supports __weakref__)."""

    def __init__(self, tag: str = "x") -> None:
        self.tag = tag


# --- WeakRef class ---


def test_weakref_returns_live_object() -> None:
    obj = _UserClass()
    r = WeakRef(obj)
    assert r.get() is obj
    assert r() is obj


def test_weakref_returns_none_after_gc() -> None:
    obj = _UserClass()
    r = WeakRef(obj)
    del obj
    gc.collect()
    assert isinstance(r.get(), NoneClass)
    assert r() is none


def test_weakref_is_alive() -> None:
    obj = _UserClass()
    r = WeakRef(obj)
    assert r.is_alive() is true
    del obj
    gc.collect()
    assert r.is_alive() is false


def test_weakref_callback_fires() -> None:
    fired: list[object] = []
    obj = _UserClass()
    r = WeakRef(obj, callback=lambda arg: fired.append(arg))
    del obj
    gc.collect()
    assert len(fired) == 1
    assert fired[0] is none
    del r


# --- weakref namespace ---


def test_weakref_ref_function() -> None:
    obj = _UserClass()
    r = Weakref.ref(obj)
    assert isinstance(r, WeakRef)
    assert r.get() is obj


def test_weakref_proxy_forwards_attribute() -> None:
    obj = _UserClass(tag="hello")
    p = Weakref.proxy(obj)
    assert p.tag == "hello"


def test_weakref_getweakrefcount() -> None:
    obj = _UserClass()
    assert Weakref.getweakrefcount(obj) == Int(0)
    _ = WeakRef(obj)
    assert Weakref.getweakrefcount(obj) == Int(1)


def test_weakref_getweakrefs_returns_list() -> None:
    obj = _UserClass()
    r = WeakRef(obj)
    refs = Weakref.getweakrefs(obj)
    assert isinstance(refs, List)
    assert refs.len() == Int(1)
    # The returned wrapper should resolve to the same object.
    first = refs.at(Int(0))
    assert isinstance(first, WeakRef)
    assert first.get() is obj
    del r  # keep `r` alive long enough for the assertion above


# --- WeakSet ---


def test_weakset_add_and_includes() -> None:
    obj = _UserClass()
    ws = WeakSet()
    ws.add(obj)
    assert ws.includes(obj) is true
    assert ws.len() == Int(1)


def test_weakset_discard_missing_ok() -> None:
    ws = WeakSet()
    assert ws.discard(_UserClass()) is none


def test_weakset_remove_present() -> None:
    obj = _UserClass()
    ws = WeakSet()
    ws.add(obj)
    ws.remove(obj)
    assert ws.includes(obj) is false


def test_weakset_remove_missing_raises() -> None:
    ws = WeakSet()
    with pytest.raises(KeyError):
        ws.remove(_UserClass())


def test_weakset_entries_disappear_after_gc() -> None:
    obj = _UserClass()
    ws = WeakSet()
    ws.add(obj)
    del obj
    gc.collect()
    assert ws.len() == Int(0)


# --- WeakKeyDictionary ---


def test_weak_key_dict_set_and_get() -> None:
    key = _UserClass()
    d = WeakKeyDictionary()
    d.at_put(key, Int(42))
    assert d.at(key) == Int(42)
    assert d.includes(key) is true


def test_weak_key_dict_get_missing_default() -> None:
    d = WeakKeyDictionary()
    assert d.get(_UserClass()) is none


def test_weak_key_dict_entry_disappears_after_gc() -> None:
    key = _UserClass()
    d = WeakKeyDictionary()
    d.at_put(key, Int(1))
    del key
    gc.collect()
    assert d.len() == Int(0)


# --- WeakValueDictionary ---


def test_weak_value_dict_set_and_get() -> None:
    value = _UserClass()
    d = WeakValueDictionary()
    d.at_put(Int(1), value)
    assert d.at(Int(1)) is value


def test_weak_value_dict_entry_disappears_after_gc() -> None:
    value = _UserClass()
    d = WeakValueDictionary()
    d.at_put(Int(1), value)
    del value
    gc.collect()
    assert d.len() == Int(0)


def test_weak_value_dict_get_default() -> None:
    d = WeakValueDictionary()
    assert d.get(Int(99)) is none


# --- Interpreter integration ---


def test_weakref_namespace_reachable_via_interpreter() -> None:
    src = "class Foo:\n    pass\nf = Foo()\nr = WeakRef(f)\nr.is_alive().print()\n"
    Interpreter().run_source(src)


def test_weakset_reachable_via_interpreter() -> None:
    src = (
        "class Foo:\n    pass\nf = Foo()\nws = WeakSet()\nws.add(f)\nws.len().print()\n"
    )
    Interpreter().run_source(src)
