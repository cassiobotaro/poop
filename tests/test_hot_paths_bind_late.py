"""No function-local import fires on the paths every program runs.

`poop/types/_late.py` says which sites bind late and why; this is the test that
keeps them so. It records every import whose caller is a function under
`poop/` while the hot operations run, and expects none — a regression names
the file and line that reintroduced one. Timing is deliberately not asserted:
CI timing is noise, and the measurement that justified the change is recorded
in the change's design document.
"""

import builtins
import contextlib
import io
import sys
from typing import TYPE_CHECKING

from poop.transformers.int import IntTransformer
from poop.types._argument import an_int
from poop.types.boolean import true
from poop.types.complex import Complex
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Mapping, Sequence
    from types import ModuleType


@contextlib.contextmanager
def _recording_imports() -> Generator[list[tuple[str, int, str]]]:
    """Every `poop/`-internal import fired from inside a function, by site."""
    fired: list[tuple[str, int, str]] = []
    real_import = builtins.__import__

    def counting(
        name: str,
        globals: Mapping[str, object] | None = None,  # noqa: A002 — `__import__`'s own names
        locals: Mapping[str, object] | None = None,  # noqa: A002
        fromlist: Sequence[str] | None = (),
        level: int = 0,
    ) -> ModuleType:
        frame = sys._getframe(1)
        code = frame.f_code
        if "poop/" in code.co_filename and code.co_name != "<module>":
            fired.append(
                (code.co_filename.split("poop/")[-1], frame.f_lineno, code.co_name)
            )
        return real_import(name, globals, locals, fromlist, level)

    # ty refuses to assign over a stub-declared function even with the same
    # signature; the swap is the point of the test.
    builtins.__import__ = counting  # ty: ignore[invalid-assignment]
    try:
        yield fired
    finally:
        builtins.__import__ = real_import


def _hot_operations() -> dict[str, Callable[[], object]]:
    a, b, f, c = Int(3), Int(4), Float(2.5), Complex(1j)
    xs = List(Int(1), Int(2), Int(3))
    s = Str("ab")
    int_alias = IntTransformer.BINDINGS["_poop_int_cls"]
    return {
        "Int < Int": lambda: a < b,
        "Int == Int": lambda: a == b,
        "Int + Int": lambda: a + b,
        "Int * Float": lambda: a * f,
        "Int ** Int": lambda: a**b,
        "Int == Complex": lambda: a == c,
        "an_int(Int)": lambda: an_int(a, "x", "r"),
        "(5).abs()": lambda: a.abs(),
        "xs.at(0)": lambda: xs.at(Int(0)),
        "xs.map(block)": lambda: xs.map(lambda x: x),
        "xs.filter(block)": lambda: xs.filter(lambda x: x),
        '"ab".len()': lambda: s.len(),
        "true.if_true(block)": lambda: true.if_true(lambda: 1),
        "obj.print()": lambda: a.print(),
        "int == int": lambda: int_alias == int_alias,
        "obj.repr()": lambda: xs.repr(),
    }


def test_the_hot_paths_fire_no_local_import() -> None:
    operations = _hot_operations()
    with contextlib.redirect_stdout(io.StringIO()):
        for run in operations.values():
            run()  # warm-up: the late getters pay their one import here
        with _recording_imports() as fired:
            for run in operations.values():
                for _ in range(3):
                    run()
    assert fired == [], "\n".join(
        f"{f}:{line}  {fn}" for f, line, fn in sorted(set(fired))
    )


def test_the_recorder_sees_a_local_import() -> None:
    """A recorder that stopped seeing imports would report a clean run."""

    def cold() -> None:
        from poop.types.tuple import Tuple  # noqa: PLC0415

        assert Tuple

    # Spelled as a function in this file, which `pytest` runs from the repo
    # root, so its filename carries `poop/` the way the wrappers' do.
    with _recording_imports() as fired:
        cold()
    assert fired and fired[0][2] == "cold"


def test_every_hot_operation_still_runs() -> None:
    """The operations are real sends, not stubs: each one answers without raising."""
    with contextlib.redirect_stdout(io.StringIO()):
        for run in _hot_operations().values():
            run()
