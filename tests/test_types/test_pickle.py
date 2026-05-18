from pathlib import Path as _PyPath

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.float import Float
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.pickle import PickleNamespace, Pickler, Unpickler
from poop.types.set import Set
from poop.types.string import Str
from poop.types.tuple import Tuple


# Pickle-safe POOP user class — no __slots__, so it has __dict__ and is
# importable by qualified name (test module is loaded normally by pytest).
class UserPoint(Object):
    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other: object) -> bool:
        return isinstance(other, UserPoint) and self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))


# --- Module-level shortcuts ---


def test_dumps_returns_bytes() -> None:
    raw = PickleNamespace.dumps(Int(42))
    assert isinstance(raw, Bytes)


def test_dumps_loads_int_round_trip() -> None:
    raw = PickleNamespace.dumps(Int(42))
    result = PickleNamespace.loads(raw)
    assert result == Int(42)
    assert isinstance(result, Int)


def test_dumps_loads_str_round_trip() -> None:
    raw = PickleNamespace.dumps(Str("hello"))
    result = PickleNamespace.loads(raw)
    assert result == Str("hello")
    assert isinstance(result, Str)


def test_dumps_loads_float_round_trip() -> None:
    raw = PickleNamespace.dumps(Float(3.14))
    result = PickleNamespace.loads(raw)
    assert isinstance(result, Float)


def test_dumps_loads_bytes_round_trip() -> None:
    raw = PickleNamespace.dumps(Bytes(b"\xff\x00"))
    result = PickleNamespace.loads(raw)
    assert result == Bytes(b"\xff\x00")


def test_dumps_loads_bool_round_trip() -> None:
    assert PickleNamespace.loads(PickleNamespace.dumps(true)) is true
    assert PickleNamespace.loads(PickleNamespace.dumps(false)) is false


def test_dumps_loads_none_round_trip() -> None:
    assert PickleNamespace.loads(PickleNamespace.dumps(none)) is none


def test_dumps_loads_list_round_trip() -> None:
    original = List(Int(1), Str("two"), Float(3.0))
    result = PickleNamespace.loads(PickleNamespace.dumps(original))
    assert result == original
    assert isinstance(result, List)


def test_dumps_loads_tuple_round_trip() -> None:
    original = Tuple(Int(1), Int(2), Int(3))
    result = PickleNamespace.loads(PickleNamespace.dumps(original))
    assert result == original
    assert isinstance(result, Tuple)


def test_dumps_loads_dict_round_trip() -> None:
    original = Dict().at_put(Str("a"), Int(1)).at_put(Str("b"), Int(2))
    result = PickleNamespace.loads(PickleNamespace.dumps(original))
    assert result == original
    assert isinstance(result, Dict)


def test_dumps_loads_set_round_trip() -> None:
    original = Set(Int(1), Int(2), Int(3))
    result = PickleNamespace.loads(PickleNamespace.dumps(original))
    assert isinstance(result, Set)
    assert result.len() == Int(3)


def test_dumps_loads_frozen_set_round_trip() -> None:
    original = FrozenSet(Int(1), Int(2))
    result = PickleNamespace.loads(PickleNamespace.dumps(original))
    assert isinstance(result, FrozenSet)


def test_dumps_loads_nested_round_trip() -> None:
    original = List(
        Dict().at_put(Str("key"), List(Int(1), Int(2))),
        Tuple(Str("x"), Int(99)),
    )
    result = PickleNamespace.loads(PickleNamespace.dumps(original))
    assert result == original


def test_dumps_with_protocol() -> None:
    raw = PickleNamespace.dumps(List(Int(1), Int(2)), protocol=Int(2))
    assert isinstance(raw, Bytes)
    assert PickleNamespace.loads(raw) == List(Int(1), Int(2))


def test_dumps_user_class_round_trips() -> None:
    raw = PickleNamespace.dumps(UserPoint(3, 4))
    result = PickleNamespace.loads(raw)
    assert isinstance(result, UserPoint)
    assert result.x == 3
    assert result.y == 4


# --- Path-based dump / load ---


def test_dump_load_round_trip(tmp_path: _PyPath) -> None:
    target = tmp_path / "data.pkl"
    PickleNamespace.dump(
        Dict().at_put(Str("x"), List(Int(1), Int(2), Int(3))),
        Path(Str(str(target))),
    )
    assert target.exists()
    restored = PickleNamespace.load(Path(Str(str(target))))
    expected = Dict().at_put(Str("x"), List(Int(1), Int(2), Int(3)))
    assert restored == expected


def test_dump_user_class_to_path(tmp_path: _PyPath) -> None:
    target = tmp_path / "point.pkl"
    PickleNamespace.dump(UserPoint(5, 9), Path(Str(str(target))))
    restored = PickleNamespace.load(Path(Str(str(target))))
    assert restored == UserPoint(5, 9)


def test_dump_returns_none(tmp_path: _PyPath) -> None:
    target = tmp_path / "x.pkl"
    assert PickleNamespace.dump(Int(7), Path(Str(str(target)))) is none


# --- Constants ---


def test_highest_protocol_is_int() -> None:
    assert isinstance(PickleNamespace.HIGHEST_PROTOCOL, Int)
    assert PickleNamespace.HIGHEST_PROTOCOL._value >= 5


def test_default_protocol_is_int() -> None:
    assert isinstance(PickleNamespace.DEFAULT_PROTOCOL, Int)


# --- Error classes ---


def test_error_classes_exposed() -> None:
    assert issubclass(PickleNamespace.PicklingError, PickleNamespace.PickleError)
    assert issubclass(PickleNamespace.UnpicklingError, PickleNamespace.PickleError)


def test_loads_corrupt_data_raises() -> None:
    with pytest.raises(PickleNamespace.UnpicklingError):
        PickleNamespace.loads(Bytes(b"not a pickle stream"))


# --- Pickler / Unpickler classes ---


def test_pickler_accumulates_multiple_dumps() -> None:
    p = Pickler()
    p.dump(Int(1))
    p.dump(Str("two"))
    p.dump(List(Int(3), Int(4)))

    raw = p.getvalue()
    assert isinstance(raw, Bytes)

    u = Unpickler(raw)
    assert u.load() == Int(1)
    assert u.load() == Str("two")
    assert u.load() == List(Int(3), Int(4))


def test_pickler_with_explicit_protocol() -> None:
    p = Pickler(protocol=Int(2))
    p.dump(Dict().at_put(Str("k"), Str("v")))
    raw = p.getvalue()
    u = Unpickler(raw)
    expected = Dict().at_put(Str("k"), Str("v"))
    assert u.load() == expected


def test_pickler_clear_memo_returns_none() -> None:
    p = Pickler()
    p.dump(List(Int(1), Int(2)))
    assert p.clear_memo() is none


def test_pickler_fast_attribute() -> None:
    # `fast` is now the inherited stdlib C-struct attribute (int 0/1) —
    # POOP no longer shimms it to Boolean because the C extension
    # bypasses Python descriptors.
    p = Pickler()
    assert p.fast == 0
    p.fast = True
    assert p.fast == 1
    p.fast = False


def test_pickler_dump_returns_none() -> None:
    p = Pickler()
    assert p.dump(Int(1)) is none


def test_unpickler_can_load_user_class() -> None:
    p = Pickler()
    p.dump(UserPoint(1, 2))
    u = Unpickler(p.getvalue())
    result = u.load()
    assert result == UserPoint(1, 2)


# --- Interpreter integration ---


def test_pickle_dumps_loads_via_interpreter() -> None:
    Interpreter().run_source("raw = pickle.dumps([1, 2, 3])\npickle.loads(raw).print()")


def test_Pickler_Unpickler_reachable_via_interpreter() -> None:
    Interpreter().run_source(
        "p = Pickler()\np.dump(42)\nUnpickler(p.getvalue()).load().print()"
    )


def test_pickle_constants_reachable_via_interpreter() -> None:
    Interpreter().run_source("pickle.HIGHEST_PROTOCOL.print()")


# --- Subclassing surface: persistent_id / persistent_load (bridge) ---


def test_pickler_persistent_id_override_in_poop_idiom() -> None:
    # When pickling a value that the override considers "external",
    # the override returns a POOP Str ID; the bridge unwraps to Python
    # str for CPython's pickle protocol, which embeds the ID instead
    # of serialising the value.
    class TaggedPickler(Pickler):
        def persistent_id(self, obj):  # type: ignore[no-untyped-def]
            if isinstance(obj, Str) and obj == Str("secret"):
                return Str("REF:secret")
            return none

    class TaggedUnpickler(Unpickler):
        def persistent_load(self, pid):  # type: ignore[no-untyped-def]
            return Str("RESOLVED:" + pid._value)

    p = TaggedPickler()
    p.dump(List(Str("public"), Str("secret"), Str("also-public")))
    raw = p.getvalue()

    u = TaggedUnpickler(raw)
    loaded = u.load()
    assert loaded == List(Str("public"), Str("RESOLVED:REF:secret"), Str("also-public"))


def test_pickler_persistent_id_none_means_pickle_normally() -> None:
    class IdleP(Pickler):
        def persistent_id(self, obj):  # type: ignore[no-untyped-def]
            return none

    p = IdleP()
    p.dump(Int(42))
    assert Unpickler(p.getvalue()).load() == Int(42)


def test_pickler_is_stdlib_pickler() -> None:
    import pickle as _stdlib_pickle

    assert issubclass(Pickler, _stdlib_pickle.Pickler)
    assert issubclass(Unpickler, _stdlib_pickle.Unpickler)


# --- dispatch_table bridge ---


def test_pickler_dispatch_table_block_reducer() -> None:
    # A reducer block receiving the obj as POOP, returning a POOP Tuple
    # describing how to reconstruct it.
    from poop.types.block import Block

    seen: list[UserPoint] = []

    def reduce_point(obj):  # type: ignore[no-untyped-def]
        seen.append(obj)
        return Tuple(UserPoint, Tuple(Int(obj.x), Int(obj.y)))  # ty: ignore[invalid-argument-type]

    p = Pickler()
    p.dispatch_table = {UserPoint: Block(reduce_point)}
    p.dump(UserPoint(7, 8))

    restored = Unpickler(p.getvalue()).load()
    assert restored == UserPoint(7, 8)
    assert seen and isinstance(seen[0], UserPoint)


def test_pickler_dispatch_table_accepts_python_callable_directly() -> None:
    # Non-Block callables pass through without bridging.
    def reduce_point(obj):  # type: ignore[no-untyped-def]
        return (UserPoint, (obj.x, obj.y))

    p = Pickler()
    p.dispatch_table = {UserPoint: reduce_point}
    p.dump(UserPoint(2, 3))
    restored = Unpickler(p.getvalue()).load()
    assert restored == UserPoint(2, 3)


def test_pickler_dispatch_table_unset_falls_back_to_default() -> None:
    p = Pickler()
    # AttributeError, not None — matches CPython's "no table" sentinel.
    with pytest.raises(AttributeError):
        _ = p.dispatch_table
    # Default behaviour still works (no reducer registered for UserPoint
    # — copyreg fallback handles user classes generically).
    p.dump(UserPoint(1, 2))
    assert Unpickler(p.getvalue()).load() == UserPoint(1, 2)


def test_pickler_dispatch_table_assigning_none_clears() -> None:
    from poop.types.block import Block

    p = Pickler()
    p.dispatch_table = {UserPoint: Block(lambda obj: (UserPoint, (obj.x, obj.y)))}
    assert isinstance(p.dispatch_table, dict)
    p.dispatch_table = None
    with pytest.raises(AttributeError):
        _ = p.dispatch_table


def test_pickler_dispatch_table_accepts_poop_dict() -> None:
    from poop.types.block import Block

    def reduce_point(obj):  # type: ignore[no-untyped-def]
        return Tuple(UserPoint, Tuple(Int(obj.x), Int(obj.y)))  # ty: ignore[invalid-argument-type]

    p = Pickler()
    table = Dict()
    table._data[UserPoint] = Block(reduce_point)  # ty: ignore[invalid-assignment]
    p.dispatch_table = table
    p.dump(UserPoint(11, 22))
    assert Unpickler(p.getvalue()).load() == UserPoint(11, 22)


def test_pickler_dispatch_table_rejects_non_dict() -> None:
    p = Pickler()
    with pytest.raises(TypeError, match="dispatch_table"):
        p.dispatch_table = [UserPoint, lambda obj: (UserPoint, (obj.x,))]


# --- PickleBuffer ---


def test_pickle_buffer_wraps_bytes() -> None:
    from poop.types.memory_view import MemoryView
    from poop.types.pickle import PickleBuffer

    buf = PickleBuffer(Bytes(b"payload"))
    raw = buf.raw()
    assert isinstance(raw, MemoryView)
    buf.release()


def test_pickle_buffer_accepts_raw_bytes() -> None:
    from poop.types.pickle import PickleBuffer

    buf = PickleBuffer(b"raw")
    assert buf.release() is none


def test_pickle_buffer_namespace_attribute_matches_class() -> None:
    from poop.types.pickle import PickleBuffer

    assert PickleNamespace.PickleBuffer is PickleBuffer
