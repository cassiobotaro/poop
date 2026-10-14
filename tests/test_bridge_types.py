"""`to_poop`'s overloads answer the POOP class for a *typed* container.

Checked by ty in the full gate; under pytest every line is a no-op. The
container overloads in `poop/types/_bridge.py` take `Any` parameters because
`dict`, `list`, `set` and `frozendict` are invariant: declared over `object`,
they matched no `dict[int, int]` a caller could hold, and every typed
container fell through to the `object -> object` overload (`tuple` and
`frozenset` escaped, being covariant). This is the test that fails, in ty,
if anyone tightens them back.
"""

from typing import assert_type

from poop.types._bridge import to_poop
from poop.types.dict import Dict
from poop.types.frozen_dict import FrozenDict
from poop.types.frozen_set import FrozenSet
from poop.types.list import List
from poop.types.set import Set
from poop.types.tuple import Tuple


def test_a_typed_container_crosses_as_its_poop_class() -> None:
    # Declared variables, not literals: ty infers a `{1: 2}` handed straight
    # to `to_poop` against the parameter it is matching (bidirectional
    # inference), so the assertion would pass on the broken overloads too.
    # A value whose type is already fixed is what a real caller holds.
    d: dict[int, int] = {1: 2}
    xs: list[int] = [1]
    t: tuple[int, int] = (1, 2)
    s: set[str] = {"a"}
    fs: frozenset[str] = frozenset({"a"})
    fd: frozendict[str, int] = frozendict(a=1)
    assert_type(to_poop(d), Dict)
    assert_type(to_poop(xs), List)
    assert_type(to_poop(t), Tuple)
    assert_type(to_poop(s), Set)
    assert_type(to_poop(fs), FrozenSet)
    assert_type(to_poop(fd), FrozenDict)
    # The caller that found the gap: `str.maketrans` answers a `dict[int, int]`.
    assert_type(to_poop(str.maketrans("a", "b")), Dict)
    # And the answers are real, not only well-typed.
    assert to_poop(d) == Dict().at_put(to_poop(1), to_poop(2))
    assert to_poop(xs) == List(to_poop(1))
