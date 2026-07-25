from poop.types._index import Index
from poop.types.boolean import Boolean
from poop.types.int import Int


def test_index_names_both_rungs_of_the_index_protocol() -> None:
    # `bool` is an `int` subclass in CPython, but POOP's Boolean is not an Int
    # subclass, so the alias has to name both — and both answer __index__.
    assert Index.__value__ == Int | Boolean
