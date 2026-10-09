import ast
import inspect

import poop.types._index
from poop.types._index import Index


def test_index_names_both_rungs_of_the_index_protocol() -> None:
    # `bool` is an `int` subclass in CPython, but POOP's Boolean is not an Int
    # subclass, so the alias has to name both — and both answer __index__.
    # Pinned on the source rather than on `Index.__value__`: the alias is read
    # by `ty` and never evaluated, and evaluating it would send `|` to the
    # class side, which refuses every operator under the class's own name.
    module = ast.parse(inspect.getsource(poop.types._index))
    alias = next(node for node in module.body if isinstance(node, ast.TypeAlias))
    assert alias.name.id == Index.__name__ == "Index"
    assert ast.unparse(alias.value) == "Int | Boolean"
