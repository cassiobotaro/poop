"""No failure a program can reach describes a construct POOP forbids.

The rewordings live in nine wrappers, two transformers and one translation
step, and each was verified where it was written. This is the test that says
they add up: it runs failing programs end to end, through the same path a user
sees, and refuses the phrases that name Python's constructs rather than POOP's
messages.

A per-site assertion cannot do this — the next wrapper is free to reintroduce
any of them, which is how the ten proposals accumulated in the first place.
"""

import ast
import pathlib
import re

import pytest

from poop import Interpreter
from poop.errors import PoopError

# Each pattern names a construct POOP does not have. `indices` and `index out
# of range` describe subscripting (no_subscript); `operand type(s)` and `not
# supported between instances` describe an operator as a type-level protocol
# rather than a message; `<lambda>` and `positional argument` describe a
# block as a Python function; `word()` is a method spelt as a call.
_FORBIDDEN = {
    "subscripting": re.compile(r"indices|index out of range|out of bounds"),
    "operator-as-protocol": re.compile(
        r"operand type\(s\)|not supported between instances"
    ),
    "a block as a function": re.compile(r"<lambda>|positional argument"),
    "a message as a call": re.compile(r"\b\w+\(\)|\b\w+\.\w+\("),
    "a banned dunder": re.compile(r"__\w+__"),
    "a generator": re.compile(r"\bgenerator\b|\byield\b"),
}

# Programs whose failure a reader is meant to understand. Kept as source, not
# as calls into the types, so the assertion covers the whole path — including
# `_describe`, which is where the operator translation runs.
_FAILING = [
    '"abc".at(10)',
    '"abc".at("x")',
    "[1, 2].at(9)",
    '[1, 2].at("x")',
    "(1, 2).at(9)",
    'b"ab".at(9)',
    'bytearray(b"ab").at(9)',
    "range(3).at(9)",
    'memoryview(b"ab").at(9)',
    '{"a": 1}.at("b")',
    "[].pop()",
    "[1, 2].pop(9)",
    "[1, 2].index(9)",
    "(1, 2).index(9)",
    "range(5).index(9)",
    'memoryview(b"ab").index(9)',
    'b"ab".ord()',
    '"ab".ord()',
    "[1, 2].remove(9)",
    # `del_attr` was the one member of the getattr-substitute family with no
    # refusal of its own, so CPython named `__dict__` — the dunder
    # `_reject_dunder` will not even let a program spell.
    '"abc".del_attr("zzz")',
    # A method read by *writing* it stayed a native bound method, so asking it
    # anything answered `'function' object has no attribute 'print'` — the
    # value described as exactly the kind of thing a block is, then refusing
    # what every block answers.
    '"abc".upper.nope()',
    "[1].del_attr('append')",
    # `has_next` exists so exhaustion can be *asked* about; it answered
    # `dictionary changed size during iteration`, which `next` reworded.
    'd = {"a": 1}\nit = d.iter()\nit.next()\nd.at_put("b", 2)\nit.has_next()',
    # The `r`-prefixed searches were left on `_faithful`, so the same mistake
    # one letter apart answered in two vocabularies.
    '"abc".rfind(lambda c: c)',
    '"abc".rindex(lambda c: c)',
    # `pow() 3rd argument cannot be 0` names the builtin `no_pow` forbids; the
    # float form answered CPython's *signature* instead of the operation.
    "(2).pow(3, 0)",
    "(2.0).pow(3, 5)",
    # The six removals: `popitem()`, `pop from …` and `bytearray` are exactly
    # what this sweep is for, and three answered a bare repr with no sentence.
    '{"a": 1}.pop("b")',
    "{}.popitem()",
    "{1}.remove(2)",
    "set().pop()",
    "bytearray().pop()",
    'bytearray(b"a").remove(98)',
    '"abc".slice(slice("a", 2))',
    '[1, 2].slice(slice("a", 2))',
    # A constructor call the converter could not take used to fall through to
    # the wrapper class, whose `__init__` CPython then named.
    "list(1, 2)",
    'complex("abc")',
    "complex([1], 2)",
    "(-1).chr()",
    'd = {"a": 1}\nd.do(lambda p: d.at_put("b", 2))',
    'str(b"ab", "utf-8", "strict", 1)',
    "memoryview(b'ab', 1)",
    'int("abc")',
    'float("abc")',
    'int("ff", 99)',
    "[].min()",
    "[].max()",
    "[1, 2].zip([1], strict=True).do(lambda p: p.print())",
    '[1, "a"].sorted()',
    '[1, "a"].min()',
    '[1, "a"].max()',
    '("a" + 1)',
    '(1 + "a")',
    '(1 < "a")',
    "([1] + 1)",
    '(2 ** "a")',
    '(5).divmod("a")',
    "b = lambda x: x\nb(1, 2)",
    # PEP 479 turned this into `generator raised StopIteration` — a report
    # about a construct POOP does not have and no_yield bans.
    "i = [1].iter()\nlist([1, 2, 3].map(lambda v: i.next()))",
    "i = [1].iter()\nlist([1, 2, 3].filter(lambda v: i.next()))",
    "i = [1].iter()\ni.next()\ni.next()",
    "b = lambda: 1\nb(9)",
    # The two constructs `DEFAULT_NAMESPACE` hands users directly: a non-block
    # was reported by CPython's call machinery, one frame deep.
    # `Str.format` is POOP's documented template surface, and every one of
    # its failures was CPython's: a bare `KeyError: 'a'`, an index error
    # naming the "positional args tuple", and a spec error naming a "format
    # code" for an "object of type". The sweep varies *arguments*, never the
    # receiver's own text, which is why it never saw these.
    '"{a}".format(b=1)',
    '"{}".format()',
    '"{}{}".format(1)',
    '"{:d}".format("a")',
    '"{".format()',
    "Try(5).run()",
    "Try(lambda: 1).except_(Exception, 5)",
    "With(5).do(lambda x: x)",
    # A receiver that cannot be entered, and one that can be entered but never
    # exited: CPython names the missing dunder in both.
    "With(lambda: 5).do(lambda x: x)",
    "class C(Object):\n    def __enter__(self):\n        return 1\n"
    "With(lambda: C()).do(lambda x: x)",
]


def _failure(source: str) -> str:
    with pytest.raises(PoopError) as info:
        Interpreter().run_source(source)
    return str(info.value)


@pytest.mark.parametrize("source", _FAILING)
def test_no_failure_names_a_forbidden_construct(source: str) -> None:
    message = _failure(source)
    named = [
        construct
        for construct, pattern in _FORBIDDEN.items()
        if pattern.search(message)
    ]
    assert named == [], f"{source!r} answered {message!r}, naming {named}"


@pytest.mark.parametrize("source", _FAILING)
def test_every_failure_still_says_something(source: str) -> None:
    """Guards the sweep: an empty message passes every pattern above."""
    message = _failure(source).split(": ", 1)[-1]
    assert len(message.split()) >= 3


def test_the_sweep_would_catch_a_regression() -> None:
    """The patterns are not vacuous — CPython's own wording trips them."""
    leaked = "TypeError: unsupported operand type(s) for +: 'str' and 'int'"
    assert _FORBIDDEN["operator-as-protocol"].search(leaked)
    assert _FORBIDDEN["subscripting"].search("IndexError: list index out of range")
    assert _FORBIDDEN["a message as a call"].search("list.index(x): x not in list")


# --- the static half: every message POOP *writes* itself ---
#
# The list above is opt-in by program, so a leak survives simply by not being
# on it — which is how three of these accumulated. The POOP-authored half is
# statically checkable: walk the packages for the string literals handed to a
# `MIRRORS[...]` call and run the same patterns over them. That catches a new
# `complex()` the day it is written, without anyone remembering to add a
# program. The same argument `tests/test_mirrored_raises.py` makes for the
# *class* half of the rule.

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_PACKAGES = ("poop/types", "poop/transformers")

# A message may legitimately quote the POOP spelling the reader should write,
# and a POOP message shown with its arguments looks like a Python call to the
# patterns above. Listed as fragments, so an exemption says which *phrase* is
# sanctioned rather than blessing a whole message forever.
_EXEMPT: tuple[str, ...] = ("obj.get_attr(...) / obj.at(...)",)


def _mirror_messages() -> list[tuple[pathlib.Path, int, str]]:
    """Every string literal handed to a `MIRRORS[...]` call, with its site."""
    found: list[tuple[pathlib.Path, int, str]] = []
    for package in _PACKAGES:
        for path in sorted((_ROOT / package).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not _is_mirror(node.func):
                    continue
                for arg in node.args:
                    text = _literal_text(arg)
                    if text:
                        found.append((path, node.lineno, text))
    return found


def _is_mirror(func: ast.expr) -> bool:
    return (
        isinstance(func, ast.Subscript)
        and isinstance(func.value, ast.Name)
        and func.value.id == "MIRRORS"
    )


def _literal_text(node: ast.expr) -> str:
    """The literal parts of `node` — an f-string's placeholders are unknown."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(
            part.value
            for part in node.values
            if isinstance(part, ast.Constant) and isinstance(part.value, str)
        )
    return ""


def test_the_static_sweep_finds_the_messages() -> None:
    """A walker that stopped matching would report a clean run."""
    assert len(_mirror_messages()) > 30


@pytest.mark.parametrize(
    ("path", "lineno", "message"),
    _mirror_messages(),
    ids=lambda arg: f"{arg.name}" if isinstance(arg, pathlib.Path) else str(arg)[:40],
)
def test_no_poop_authored_message_names_a_forbidden_construct(
    path: pathlib.Path, lineno: int, message: str
) -> None:
    if any(fragment in message for fragment in _EXEMPT):
        return
    named = [
        construct
        for construct, pattern in _FORBIDDEN.items()
        if pattern.search(message)
    ]
    assert named == [], (
        f"{path.relative_to(_ROOT)}:{lineno} composes {message!r}, naming {named}"
    )


# --- the mechanical half: every message, sent wrong ---
#
# `_FAILING` above is opt-in *by program*, which its own docstring calls the
# weak half ("a leak survives simply by not being on it"). Items 3, 5, 6, 7 and
# 8 of the backlog were each found by writing one more program by hand. This
# sweeps instead: every public message on every wrapper, called with
# wrong-typed arguments, checked with the same patterns. It found 47 distinct
# leaks across 114 receiver/message sites the day it was written, and it keeps
# finding the next one without anyone remembering to add a program.

_SAMPLES: dict[str, object] = {}


def _receivers() -> dict[str, object]:
    """One live value per wrapper, built the way a program would."""
    if _SAMPLES:
        return _SAMPLES
    from poop.types.boolean import true
    from poop.types.byte_array import ByteArray
    from poop.types.bytes import Bytes
    from poop.types.complex import Complex
    from poop.types.dict import Dict
    from poop.types.float import Float
    from poop.types.frozen_set import FrozenSet
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.none import none
    from poop.types.range import Range
    from poop.types.set import Set
    from poop.types.slice import Slice
    from poop.types.string import Str
    from poop.types.tuple import Tuple

    mapping = Dict()
    mapping.at_put(Str("a"), Int(1))
    _SAMPLES.update(
        {
            "int": Int(5),
            "float": Float(2.5),
            "complex": Complex(complex(1, 2)),
            "bool": true,
            "str": Str("abc"),
            "bytes": Bytes(b"ab"),
            "bytearray": ByteArray(bytearray(b"ab")),
            "list": List(Int(1), Int(2)),
            "tuple": Tuple(Int(1), Int(2)),
            "dict": mapping,
            "set": Set(Int(1)),
            "frozenset": FrozenSet(Int(1)),
            "range": Range(Int(0), Int(3)),
            "slice": Slice(Int(0), Int(2)),
            "none": none,
        }
    )
    return _SAMPLES


def _wrong_arguments() -> list[object]:
    from poop.types.block import Block
    from poop.types.boolean import true
    from poop.types.dict import Dict
    from poop.types.int import Int
    from poop.types.list import List
    from poop.types.none import none
    from poop.types.string import Str

    return [Str("zz"), Int(3), List(Int(1)), Block(lambda x: x), true, none, Dict()]


# CPython's wrong-arity report is the one shape deliberately left to it:
# `_cloak`'s docstring says so, and it only renames the callee. Everything
# else is POOP's to word.
_ARITY = re.compile(
    r"(takes|missing|got) .*(positional argument|argument)|"
    r"takes no arguments|"
    r"expected \d+ arguments"
)

# Messages that must not be *sent* by the sweep: they block, exit, or mutate
# the shared sample in a way later cases would read.
_UNSENDABLE = frozenset(
    {"input", "print", "does_not_understand", "while_true", "while_false"}
)


def _sweep_failures() -> list[tuple[str, str, str]]:
    """(receiver, message, text) for every leak the wrong-argument sweep finds."""
    from poop.types._message import poop_message
    from poop.types._selectors import is_message

    found: dict[tuple[str, str], tuple[str, str, str]] = {}
    for label, receiver in _receivers().items():
        for name in sorted(dir(receiver)):
            if not is_message(name) or name in _UNSENDABLE:
                continue
            message = getattr(receiver, name, None)
            if not callable(message):
                continue
            for bad in _wrong_arguments():
                for args in ((bad,), (bad, bad)):
                    try:
                        message(*args)
                    except BaseException as exc:  # noqa: BLE001
                        text = poop_message(exc)
                        if _ARITY.search(text) or any(f in text for f in _EXEMPT):
                            continue
                        named = [
                            construct
                            for construct, pattern in _FORBIDDEN.items()
                            if pattern.search(text)
                        ]
                        if named:
                            found.setdefault((label, name), (label, name, text))
    return sorted(found.values())


def test_no_message_leaks_pythons_wording_when_sent_wrong() -> None:
    leaks = _sweep_failures()
    assert leaks == [], "\n".join(
        f"{label}.{name} -> {text!r}" for label, name, text in leaks
    )


def test_the_sweep_actually_sends_messages() -> None:
    """A sweep that stopped reaching the wrappers would report a clean run."""
    from poop.types._selectors import is_message

    sendable = sum(
        1
        for receiver in _receivers().values()
        for name in dir(receiver)
        if is_message(name) and name not in _UNSENDABLE
    )
    assert sendable > 500
