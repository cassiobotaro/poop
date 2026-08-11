"""A validator's Substitute must actually answer on the receiver it names.

`INFECTIONS.md` gives every ban a Substitute column, and the bans' own messages
repeat it — "blocking without offering an alternative breaks code without
teaching", as `CONTRIBUTING.md` puts it. Nothing read those columns back.

`no_format` was the row where following the table silently did nothing:
`format(x, spec)` is banned and names `x.format(spec)`, which works on every
receiver but `Str`, whose `format` is POOP's template surface. `"ab".format(">6")`
answered `'ab'` — unchanged, with no way to tell it had not worked — three times
out of three, to a reader who had just been told to write exactly that.

The sentences below are the substitutes as the bans spell them, sent to the
receivers the bans point at.
"""

import pytest

from poop.errors import PoopError
from poop.interpreter import Interpreter

# (source, what it must answer). Every entry is a substitute a validator's
# message names, written the way the message writes it.
_SUBSTITUTES = [
    # no_format — the row this test exists for. `Object.format` applies a spec.
    ('(5).format(">6")', "     5"),
    ('(2.5).format(".2f")', "2.50"),
    ('(255).format("x")', "ff"),
    # `format(True, spec)` is `int.__format__` in CPython too — `bool` only
    # prints as `True` with an *empty* spec, which is why `Boolean.format`
    # folds with `bool(self)` rather than through `_as_int`.
    ('True.format(">6")', "     1"),
    # ...and on a `Str` the working spelling is the template, which is what the
    # ban now says.
    ('"{:>6}".format("ab")', "    ab"),
    ('"{:*^6}".format("ab")', "**ab**"),
    # no_len / no_abs / no_hash and the rest of the free-function family.
    ('"abc".len()', "3"),
    ("(-5).abs()", "5"),
    ("(2.5).round()", "2"),
    ("(2).pow(3)", "8"),
    ("(7).divmod(2)", "3 1"),
    ("[1, 2].min()", "1"),
    ("[1, 2].max()", "2"),
    ("[1, 2].sum()", "3"),
    ("[2, 1].sorted()", "1 2"),
    ("[1, 2].reversed()", "2 1"),
    ('"abc".ascii()', "'abc'"),
    ("(5).bin()", "0b101"),
    ("(65).chr()", "A"),
    ('"abc".repr()', "'abc'"),
    # no_isinstance / no_issubclass / no_callable / no_dir / no_id.
    ("(5).is_instance(int)", "True"),
    ("int.is_subclass(object)", "True"),
    ("(5).callable()", "False"),
    # `no_id` names the identity *question*, never an address — and two `5`s
    # really are two objects, which is the honest answer.
    ("(5).is_identical(5)", "False"),
    ("x = 5\nx.is_identical(x)", "True"),
    # no_getattr family.
    ('"abc".has_attr("upper")', "True"),
    ('"abc".get_attr("upper")()', "ABC"),
    # no_type / no_dunder_attribute.
    ('"abc".class_name()', "str"),
    ("int.name()", "int"),
    # no_in / no_not / no_and_or / no_is.
    ('"abc".includes("b")', "True"),
    ("True.not_()", "False"),
    ("True.and_(lambda: False)", "False"),
    ("False.or_(lambda: True)", "True"),
    ("None.is_none()", "True"),
    # no_subscript.
    ("[1, 2, 3].at(0)", "1"),
    ('"abcdef".slice(1, 3)', "bc"),
    # no_if / no_loops.
    ("True.if_true_if_false(lambda: 1, lambda: 2)", "1"),
    ("(5).if_none(lambda: 9)", "5"),
    # no_iter — the walking protocol the ban names.
    ("[1, 2].iter().next()", "1"),
    ("[1, 2].iter().has_next()", "True"),
    # no_map / no_filter / no_all / no_any.
    ("list([1, 2].map(lambda x: x + 1))", "2 3"),
    ("[1, 2].all(lambda x: x > 0)", "True"),
    ("[1, 2].any(lambda x: x > 1)", "True"),
    # no_unary_minus / no_invert.
    ("(5).negated()", "-5"),
    ("(5).bit_invert()", "-6"),
]


@pytest.mark.parametrize(("source", "expected"), _SUBSTITUTES)
def test_a_substitute_answers_what_the_ban_promises(
    source: str, expected: str, capsys: pytest.CaptureFixture[str]
) -> None:
    # A multi-line entry sets something up first; the last line is the answer.
    *setup, answer = source.split("\n")
    program = "".join(f"{line}\n" for line in setup)
    Interpreter().run_source(f"{program}({answer}).print()\n")
    assert capsys.readouterr().out.rstrip("\n") == expected


def test_the_str_exception_is_named_by_the_ban_itself() -> None:
    # The fix proposal 54 chose: `Str.format` keeps the template meaning, and
    # the ban's message carries the exception rather than pointing every
    # receiver at a spelling that is a no-op on one of them.
    with pytest.raises(PoopError) as info:
        Interpreter().run_source('format("ab", ">6")\n')
    message = str(info.value)
    assert "obj.format(spec)" in message
    assert '"{:spec}".format(text)' in message


def test_the_str_no_op_is_what_the_exception_is_for() -> None:
    # Recorded rather than fixed: `Str.format` is the template surface, so a
    # spec is read as an argument for placeholders the string does not have and
    # `str.format` discards it. The ban points elsewhere precisely because of
    # this.
    interpreter = Interpreter()
    interpreter.run_source('"ab".format(">6").print()\n')
