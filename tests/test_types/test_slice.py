from poop.types.boolean import false, true
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.range import Range
from poop.types.slice import Slice
from poop.types.string import Str
from poop.types.tuple import Tuple

# --- construction ---


def test_two_arg_construction() -> None:
    s = Slice(Int(0), Int(5))
    assert s._start == Int(0)
    assert s._stop == Int(5)
    assert s._step is None


def test_three_arg_construction() -> None:
    s = Slice(Int(0), Int(10), Int(2))
    assert s._start == Int(0)
    assert s._stop == Int(10)
    assert s._step == Int(2)


# --- accessors ---


def test_start() -> None:
    assert Slice(Int(1), Int(4)).start() == Int(1)


def test_stop() -> None:
    assert Slice(Int(1), Int(4)).stop() == Int(4)


def test_step_returns_none_when_not_set() -> None:
    assert Slice(Int(0), Int(5)).step() is none


def test_step_returns_int_when_set() -> None:
    assert Slice(Int(0), Int(10), Int(3)).step() == Int(3)


# --- indices ---


def test_indices_basic() -> None:
    assert Slice(Int(0), Int(3)).indices(Int(5)) == Tuple(Int(0), Int(3), Int(1))


def test_indices_with_step() -> None:
    assert Slice(Int(0), Int(10), Int(2)).indices(Int(5)) == Tuple(
        Int(0), Int(5), Int(2)
    )


def test_indices_clamps_stop() -> None:
    assert Slice(Int(0), Int(100)).indices(Int(5)) == Tuple(Int(0), Int(5), Int(1))


def test_indices_negative_start() -> None:
    result = Slice(Int(-2), Int(5)).indices(Int(5))
    assert result == Tuple(Int(3), Int(5), Int(1))


# --- equality and hash ---


def test_equal_slices() -> None:
    assert Slice(Int(0), Int(5)) == Slice(Int(0), Int(5))


def test_equal_slices_with_step() -> None:
    assert Slice(Int(0), Int(10), Int(2)) == Slice(Int(0), Int(10), Int(2))


def test_different_start() -> None:
    assert Slice(Int(1), Int(5)) != Slice(Int(0), Int(5))


def test_different_stop() -> None:
    assert Slice(Int(0), Int(4)) != Slice(Int(0), Int(5))


def test_different_step() -> None:
    assert Slice(Int(0), Int(10), Int(2)) != Slice(Int(0), Int(10), Int(3))


def test_step_vs_no_step() -> None:
    assert Slice(Int(0), Int(5)) != Slice(Int(0), Int(5), Int(1))


def test_ne_non_slice() -> None:
    assert (Slice(Int(0), Int(5)) != Int(0)) is true


def test_eq_non_slice() -> None:
    assert (Slice(Int(0), Int(5)) == Int(0)) is false


def test_hash_equal_slices() -> None:
    assert hash(Slice(Int(0), Int(5))) == hash(Slice(Int(0), Int(5)))


def test_hashable_usable_as_dict_key() -> None:
    d = {Slice(Int(0), Int(3)): "window"}
    assert d[Slice(Int(0), Int(3))] == "window"


# --- repr / str ---


def test_str_two_arg() -> None:
    # Mirrors Python's `repr(slice(0, 5))` → "slice(0, 5, None)".
    assert str(Slice(Int(0), Int(5))) == "slice(0, 5, None)"


def test_str_three_arg() -> None:
    assert str(Slice(Int(0), Int(5), Int(2))) == "slice(0, 5, 2)"


def test_repr_equals_str() -> None:
    s = Slice(Int(1), Int(4))
    assert repr(s) == str(s)


# --- apply via obj.slice(Slice) ---


def test_list_slice_with_slice_object() -> None:
    s = Slice(Int(1), Int(4))
    assert List(Int(0), Int(1), Int(2), Int(3), Int(4)).slice(s) == List(
        Int(1), Int(2), Int(3)
    )


def test_list_slice_with_step() -> None:
    s = Slice(Int(0), Int(5), Int(2))
    assert List(Int(0), Int(1), Int(2), Int(3), Int(4)).slice(s) == List(
        Int(0), Int(2), Int(4)
    )


def test_tuple_slice_with_slice_object() -> None:
    s = Slice(Int(1), Int(3))
    assert Tuple(Int(10), Int(20), Int(30), Int(40)).slice(s) == Tuple(Int(20), Int(30))


def test_str_slice_with_slice_object() -> None:
    s = Slice(Int(1), Int(4))
    assert Str("hello").slice(s) == Str("ell")


def test_str_slice_with_step() -> None:
    s = Slice(Int(0), Int(5), Int(2))
    assert Str("hello").slice(s) == Str("hlo")


def test_bytes_slice_with_slice_object() -> None:
    s = Slice(Int(0), Int(3))
    assert Bytes(b"abcde").slice(s) == Bytes(b"abc")


def test_byte_array_slice_with_slice_object() -> None:
    s = Slice(Int(1), Int(3))
    assert ByteArray(bytearray(b"abcd")).slice(s) == ByteArray(bytearray(b"bc"))


def test_range_slice_with_slice_object() -> None:
    s = Slice(Int(1), Int(4))
    assert Range(Int(0), Int(9)).slice(s) == List(Int(1), Int(2), Int(3))


# --- reuse across collections ---


def test_same_slice_applied_to_multiple_collections() -> None:
    window = Slice(Int(0), Int(3))
    assert List(Int(10), Int(20), Int(30), Int(40), Int(50)).slice(window) == List(
        Int(10), Int(20), Int(30)
    )
    assert Str("POOP").slice(window) == Str("POO")


# --- None / none for start/stop/step ---


def test_slice_none_start_means_from_beginning() -> None:
    s = Slice(None, Int(3))
    assert s._start is None
    assert s._stop == Int(3)
    assert List(Int(1), Int(2), Int(3), Int(4)).slice(s) == List(Int(1), Int(2), Int(3))


def test_slice_none_stop_means_to_end() -> None:
    s = Slice(Int(1), None)
    assert s._start == Int(1)
    assert s._stop is None
    assert List(Int(1), Int(2), Int(3)).slice(s) == List(Int(2), Int(3))


def test_slice_all_none_is_full_copy() -> None:
    s = Slice()
    assert List(Int(1), Int(2), Int(3)).slice(s) == List(Int(1), Int(2), Int(3))


def test_slice_accepts_poop_none() -> None:
    s = Slice(none, Int(2))
    assert s._start is None
    assert List(Int(1), Int(2), Int(3)).slice(s) == List(Int(1), Int(2))


def test_slice_accessors_return_none_when_unset() -> None:
    s = Slice(None, Int(5))
    assert s.start() is none
    assert s.stop() == Int(5)


def test_slice_indices_with_none() -> None:
    assert Slice(None, Int(3)).indices(Int(5)) == Tuple(Int(0), Int(3), Int(1))
    assert Slice(Int(1), None).indices(Int(5)) == Tuple(Int(1), Int(5), Int(1))


def test_slice_str_with_none() -> None:
    assert str(Slice(None, Int(3))) == "slice(None, 3, None)"
    assert str(Slice(None, None, Int(2))) == "slice(None, None, 2)"


def test_slice_with_none_step_negative_reverses() -> None:
    s = Slice(None, None, Int(-1))
    assert List(Int(1), Int(2), Int(3)).slice(s) == List(Int(3), Int(2), Int(1))


def test_slice_eq_with_none_fields() -> None:
    assert Slice(None, Int(3)) == Slice(None, Int(3))
    assert Slice(None, Int(3)) != Slice(Int(0), Int(3))


def test_a_boolean_component_indexes_like_one() -> None:
    # slice(True, ...) is valid in CPython; the components are resolved
    # through __index__ by the sequence being sliced.
    assert List(Int(1), Int(2), Int(3)).slice(Slice(true, Int(3))) == List(
        Int(2), Int(3)
    )


def test_indices_accepts_a_boolean_length() -> None:
    assert Slice(Int(0), Int(2)).indices(true) == Tuple(Int(0), Int(1), Int(1))
