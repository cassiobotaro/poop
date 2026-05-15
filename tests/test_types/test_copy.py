import copy as _copy

from poop.interpreter import Interpreter
from poop.types.copy import Copy
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str


def test_copy_list_returns_new_instance() -> None:
    original = List(Int(1), Int(2), Int(3))
    duplicated = Copy.copy(original)
    assert duplicated is not original
    assert duplicated == original


def test_copy_is_shallow() -> None:
    inner = List(Int(1), Int(2))
    original = List(inner, Int(3))
    duplicated = Copy.copy(original)
    # First element is the same inner List (shallow).
    assert duplicated.at(Int(0)) is original.at(Int(0))


def test_deepcopy_creates_independent_inner() -> None:
    inner = List(Int(1), Int(2))
    original = List(inner, Int(3))
    duplicated = Copy.deepcopy(original)
    assert duplicated == original
    assert duplicated.at(Int(0)) is not original.at(Int(0))
    assert duplicated.at(Int(0)) == original.at(Int(0))


def test_copy_dict() -> None:
    d = Dict().at_put(Str("a"), Int(1))
    dup = Copy.copy(d)
    assert dup == d
    assert dup is not d


def test_deepcopy_dict_of_lists() -> None:
    inner = List(Int(1), Int(2))
    d = Dict().at_put(Str("nums"), inner)
    dup = Copy.deepcopy(d)
    assert dup == d
    # Inner list is a different object.
    assert dup.at(Str("nums")) is not inner


def test_copy_returns_same_type() -> None:
    s = Str("hello")
    assert isinstance(Copy.copy(s), Str)


def test_error_is_python_exception_class() -> None:
    assert Copy.Error is _copy.Error


def test_copy_reachable_via_interpreter() -> None:
    Interpreter().run_source("copy.copy([1, 2, 3]).len().print()")


def test_deepcopy_reachable_via_interpreter() -> None:
    Interpreter().run_source("copy.deepcopy([[1, 2], 3]).len().print()")
