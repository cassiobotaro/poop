"""`late`: the import that runs once, on the paths every program runs."""

import sys

from poop.types._late import late
from poop.types.int import Int


def test_a_late_getter_resolves_the_name() -> None:
    assert late("poop.types.int", "Int")() is Int


def test_a_late_getter_answers_the_same_object_twice() -> None:
    getter = late("poop.types.boolean", "to_boolean")
    assert getter() is getter()


def test_a_late_getter_may_be_built_before_its_module_is_imported() -> None:
    # The hot sites build their getters at module level, when the module they
    # name may still be mid-import or not started: nothing runs until the
    # first call, so the cycle the local import broke stays broken. A stdlib
    # module stands in for one of POOP's: re-importing a POOP module would
    # mint a second copy of its class behind the running interpreter's back.
    sys.modules.pop("colorsys", None)
    getter = late("colorsys", "rgb_to_hsv")
    assert "colorsys" not in sys.modules
    assert getter()(0.0, 0.0, 0.0) == (0.0, 0.0, 0.0)
    assert "colorsys" in sys.modules
