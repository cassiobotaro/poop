"""POOP offers one formatting message under two syntaxes; they must agree.

``no_format`` bans ``format(x, spec)`` and names ``x.format(spec)``. The
template ``"{0:spec}".format(x)`` is the other spelling of the same act, and
only one of them was worded: ``_template_refusal`` was wired into ``Str.format``
and nowhere else, so ``"{0:d}".format(2.5)`` answered ``a float cannot be
formatted with 'd'`` while ``(2.5).format("d")`` answered CPython's ``Unknown
format code 'd' for object of type 'float'`` — and the leaking half was the one
the validator sends the reader to.

No test compared the two paths against each other, which is why they could
drift. This one does exactly that, and adds the pattern the wording sweep could
not see: ``object of type 'int'`` carries no call, no dunder and no operator.
"""

import re

import pytest

from poop.errors import ExecutionError
from poop.interpreter import Interpreter

# The shapes CPython raises from a format spec. None of them is a call, a
# dunder or an operator, so `tests/test_no_python_wording.py` cannot see them.
_CPYTHON = re.compile(
    r"object of type|Unknown format code|Invalid format specifier|"
    r"Unknown conversion specifier"
)

_VALUES = ["5", "2.5", '"ab"', "True", "1 + 2j", 'b"ab"', "[1]", '{"a": 1}', "None"]
_SPECS = ["d", "s", "f", "x", "zzz", "+", "e", ">6", ".2f"]


def _answer(source: str) -> str:
    """What the program answers: `ok` or the failure's sentence."""
    try:
        Interpreter().run_source(f"x = {source}\n")
    except ExecutionError as exc:
        return str(exc).rsplit(" (line", 1)[0]
    return "ok"


@pytest.mark.parametrize("value", _VALUES)
@pytest.mark.parametrize("spec", _SPECS)
def test_the_two_spellings_agree(value: str, spec: str) -> None:
    message = _answer(f"({value}).format({spec!r})")
    template = _answer(f'"{{0:{spec}}}".format({value})')
    if message == "ok" or template == "ok":
        # `Str` is the documented exception — its `format` is the template
        # surface, which proposal 54 is about. Everything else must fail or
        # succeed together.
        return
    assert message == template, (
        f'({value}).format({spec!r}) and "{{0:{spec}}}".format({value}) '
        f"answer differently"
    )


@pytest.mark.parametrize("value", _VALUES)
@pytest.mark.parametrize("spec", _SPECS)
def test_neither_spelling_answers_a_cpython_format_sentence(
    value: str, spec: str
) -> None:
    for source in (
        f"({value}).format({spec!r})",
        f'"{{0:{spec}}}".format({value})',
    ):
        answer = _answer(source)
        found = _CPYTHON.search(answer)
        assert found is None, f"{source} answers CPython's wording: {answer}"


def test_an_unparseable_spec_is_worded_on_both_spellings() -> None:
    # `Invalid format specifier` leaked on *both* paths: `_template_refusal`
    # matched only the `Unknown format code` shape, and its fallback rewrites
    # `format string`, which this sentence does not contain.
    expected = "'zzz' is not a format spec an int understands"
    assert _answer('(5).format("zzz")') == f"ValueError: {expected}"
    assert _answer('"{0:zzz}".format(5)') == f"ValueError: {expected}"


def test_a_rejected_code_is_worded_on_both_spellings() -> None:
    expected = "a float cannot be formatted with 'd'"
    assert _answer('(2.5).format("d")') == f"ValueError: {expected}"
    assert _answer('"{0:d}".format(2.5)') == f"ValueError: {expected}"


def test_a_boolean_agrees_too() -> None:
    # `Boolean.format` overrides `Object.format` for its own reason and
    # inherited the leak with the rest of the body.
    assert "Unknown format code" not in _answer('(True).format("s")')
    assert "Invalid format specifier" not in _answer('(True).format("zzz")')


def test_a_spec_that_works_still_works() -> None:
    assert _answer('(5).format(">6")') == "ok"
    assert _answer('(2.5).format(".2f")') == "ok"
    assert _answer('"{0:>6}".format(5)') == "ok"
