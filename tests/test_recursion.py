"""Recursion is POOP's substitute for a loop, so its ceiling is POOP's problem.

`INFECTIONS.md` mirrors `RecursionError` because "recursion is POOP's substitute
for every loop, which makes it the most reachable of the lot". The class was
mirrored, the failure was catchable, and the budget it ran against had never
been looked at: one POOP message send is six Python frames, so a self-sending
message ran 164 levels deep where the same recursion written as a Python
function runs 998 — both under CPython's default limit of 1000.

Only two of those six frames are the program's. The other four are POOP getting
out of its own way, and two of them are `_MethodBlock.__call__` — the
"a method read off an object is a block" feature, which cost a third of the
ceiling with the price unrecorded until now.
"""

import pytest

from poop.errors import ExecutionError
from poop.interpreter import Interpreter

_COUNTER = """class Counter(Object):
    def count(self, n):
        return (n <= 0).if_true_if_false(lambda: 0, lambda: self.count(n - 1) + 1)


Counter().count({depth}).print()
"""


def _runs(depth: int) -> bool:
    try:
        Interpreter().run_source(_COUNTER.format(depth=depth))
    except ExecutionError:
        return False
    return True


def test_a_poop_recursion_reaches_the_depth_a_python_one_does() -> None:
    # The target the limit is sized for: a POOP program gets roughly the
    # thousand levels a Python program already gets. A language should not be
    # an order of magnitude shallower than the one it is built on, least of all
    # the one that banned `for`.
    assert _runs(900)


def test_the_old_ceiling_is_well_clear() -> None:
    # 164 was the measured depth before the limit was sized from the frame
    # cost. Anything at or below it must now be unremarkable.
    assert _runs(164)
    assert _runs(300)


def test_running_out_is_still_a_catchable_error() -> None:
    # The floor under the raised ceiling: CPython 3.14 guards the C stack
    # separately and answers a `RecursionError` rather than crashing, which is
    # what makes raising the limit safe rather than a gamble.
    with pytest.raises(ExecutionError, match="RecursionError"):
        Interpreter().run_source(_COUNTER.format(depth=100_000))


def test_a_program_can_catch_it_by_name() -> None:
    Interpreter().run_source(
        "class Counter(Object):\n"
        "    def count(self, n):\n"
        "        return self.count(n + 1)\n"
        "\n"
        "Try(lambda: Counter().count(0)).except_(\n"
        '    RecursionError, lambda e: "caught".print()\n'
        ").run()\n"
    )


def test_the_refusal_names_the_substitutes_by_shape() -> None:
    # CPython's `maximum recursion depth exceeded` names no receiver, offers no
    # substitute, and states a limit measured in Python frames — six of which
    # go to one POOP message send.
    with pytest.raises(ExecutionError) as info:
        Interpreter().run_source(_COUNTER.format(depth=100_000))
    message = str(info.value)
    assert "while_true" in message
    assert "col.do(" in message
    assert "maximum recursion depth exceeded" not in message
    assert "Stack overflow" not in message


def test_the_loop_substitutes_have_no_ceiling_at_all() -> None:
    # `while_true` and `while_false` are real Python `while` loops, which is why
    # this item is about *structural* recursion and `collatz.py` is safe at any
    # input. Ten thousand iterations would be far past any recursion limit.
    Interpreter().run_source(
        "class C(Object):\n"
        "    def init(self):\n"
        "        self._n = 0\n"
        "        return self\n"
        "    def run(self):\n"
        "        (lambda: self._n < 10000).while_true(lambda: self.step())\n"
        "        return self._n\n"
        "    def step(self):\n"
        "        self._n = self._n + 1\n"
        "\n"
        "C().init().run().print()\n"
    )
