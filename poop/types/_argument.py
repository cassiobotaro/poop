"""Argument refusals worded as POOP, for the arguments many messages share.

The wrappers reworded the failures they *raise*; the ones CPython raises on
their behalf, about an argument it was handed, were left alone — and those name
the banned builtin as a call (`isinstance() arg 2 must be a type`), or
subscripting and a dunder in one breath (`slice indices must be integers or
None or have an __index__ method`). The mechanical sweep in
`tests/test_no_python_wording.py` found 47 of them across 114 sites, in a
handful of families, which is why the wording lives here rather than being
written out once per receiver.
"""

from collections.abc import Iterable
from typing import Any

from poop.types._message import article
from poop.types._raw import _faithful
from poop.types._sentinel import MISSING
from poop.types.exceptions import MIRRORS


def no_arguments(
    cls: type, args: tuple[object, ...], kwargs: dict[str, object]
) -> None:
    """Refuse a constructor call that passed anything, in CPython's words.

    For the singletons, whose `__new__` answers the one instance and so takes
    `*args` only to word the refusal: left to CPython, an extra argument named
    `__new__` or `__init__`, where `type(None)(1)` says `NoneType takes no
    arguments`.
    """
    if args or kwargs:
        raise MIRRORS["TypeError"](f"{cls.__name__}() takes no arguments")


def a_class(value: Any, selector: str) -> Any:
    """`value` when it can stand for a class, else POOP's refusal.

    `no_isinstance` bans `isinstance(x, T)` and names `x.is_instance(T)`, and
    the substitute's own failure then said `isinstance() arg 2 must be a type,
    a tuple of types, or a union` — the builtin it replaces, spelt as the call
    it replaces. `issubclass` said the same about itself.
    """
    if isinstance(value, type | tuple):
        return value
    raise MIRRORS["TypeError"](
        f"#{selector} expects a class, got {article(type(value).__name__)}"
    )


def a_bound(value: Any, selector: str, role: str) -> Any:
    """The raw `start`/`end` behind `value`, or POOP's refusal.

    The `start` / `end` of `find`, `index`, `count`, `startswith` and their
    `r`-prefixed twins are positions, and a wrong one reached CPython's
    sequence machinery: `slice indices must be integers or None or have an
    __index__ method` names subscripting (which `no_subscript` bans) and a
    dunder (which `no_dunder_attribute` bans) in a single sentence, about a
    `slice` the program never wrote. `_resolve_py_slice` guards the real
    `slice` message for the same reason; this is the same guard for the
    messages that carry bounds without one.

    Unwraps as well as guards, so a call site spells one helper where it used
    to spell `_unwrap(start, None)`. An optional `an_int`: absent is `None`.
    """
    return an_int(value, selector, role, None)


def text_like(
    value: Any,
    selector: str,
    expected: str,
    kinds: tuple[type, ...] = (str, bytes, bytearray),
) -> Any:
    """The raw value behind a text argument, or POOP's refusal.

    CPython answers `center() argument 2 must be a byte string of length 1,
    not int` and `replace() argument 1 must be str, not int` — the message
    spelt as a call, every time. `a_needle` makes the same move for the block
    case; this covers the rest of the family and the receivers that had no
    guard at all.

    `kinds` narrows what counts as text for the caller that needs it: an
    encoding name and a byte order are `str` and nothing else, so accepting
    `b"utf-8"` here would only move their refusal one line down, into the
    branch that reports a *value* — the split `byte_order` below exists to
    keep straight.
    """
    raw = _faithful(value)
    if isinstance(raw, kinds):
        return raw
    raise MIRRORS["TypeError"](
        f"#{selector} expects {expected}, got {article(type(value).__name__)}"
    )


def a_needle(
    receiver: object,
    sub: object,
    selector: str,
    expected: str,
    kinds: tuple[type, ...] = (str,),
) -> Any:
    """The substring or subsequence a search looks for, or POOP's refusal.

    `find` / `rfind` / `index` / `rindex` / `count` keep their *text* meaning on
    `Str`, `Bytes` and `ByteArray`, where `_IterableMixin`'s twins take a block
    — so a reader arriving from `[1, 2].find(block)` writes a block here.
    CPython answers `find() argument 1 must be str, not function` — the method
    as a call, and `function`, which POOP prints as `<block>`.

    The block refusal names the class the message was sent to, read from
    `receiver`. It used to be parsed out of `expected`, the phrase describing
    the *argument*, so `b"abc".count(block)` blamed "an int" — the last thing
    the argument may be, not the receiver.

    The byte receivers accept an integer as well as a subsequence, which is
    CPython's rule (`b"ab".count(97)` is 1), so `expected` carries what this
    receiver takes.
    """
    # circular: string imports _argument
    from poop.types.string import Str  # noqa: PLC0415

    if not isinstance(sub, Str) and callable(sub):
        text = str in kinds
        sought = "substring" if text else "subsequence"
        wanted = "the text to look for" if text else "what to look for"
        raise MIRRORS["TypeError"](
            f"{type(receiver).__name__}'s #{selector} searches for a {sought} — "
            f"it takes {wanted}, not a block"
        )
    raw = _faithful(sub)
    # `kinds` is the receiver's, not a fixed set: `b"ab".count("x")` must be
    # refused here rather than pass the guard and reach CPython, and the byte
    # receivers additionally take an integer (`b"ab".count(97)` is 1), which is
    # what `__index__` admits.
    if isinstance(raw, kinds) or (bytes in kinds and hasattr(raw, "__index__")):
        return raw
    raise MIRRORS["TypeError"](
        f"#{selector} expects {expected}, got {article(type(sub).__name__)}"
    )


def a_fill(value: Any, selector: str, expected: str, kinds: tuple[type, ...]) -> Any:
    """The optional fill of `center` / `ljust` / `rjust`, or POOP's refusal.

    `None` when the fill is absent. CPython words a wrong fill three ways, none
    of them POOP's: `The fill character must be a unicode character, not int`,
    `The fill character must be exactly one character long`, and on the byte
    twins `center(): argument 2 must be a byte string of length 1, not a bytes
    object of length 2` — the message spelt as a call. `Str` reached all of
    them unguarded, and the byte twins guarded the type but not the length.
    """
    # circular: _unwrap -> boolean -> _argument
    from poop.types._unwrap import _is_absent  # noqa: PLC0415

    if _is_absent(value):
        return None
    raw = text_like(value, selector, expected, kinds)
    if len(raw) != 1:
        raise MIRRORS["TypeError"](
            f"#{selector} expects {expected}, "
            f"got {article(type(value).__name__)} of length {len(raw)}"
        )
    return raw


def bytes_like(value: Any, selector: str, *, optional: bool = False) -> Any:
    """The raw bytes behind an argument, or POOP's refusal.

    The byte twins of everything `text_like` already guards on `Str`. CPython
    answered `a bytes-like object is required, not 'str'` for eleven messages
    on both byte wrappers — a sentence with no receiver, no message and no
    substitute, and one the wording sweep could not see: it carries no call, no
    dunder and no operator.
    """
    # circular: _unwrap -> boolean -> _argument
    from poop.types._unwrap import _is_absent  # noqa: PLC0415

    # `optional` for the strip family, whose argument is genuinely absent by
    # default — CPython's own `strip arg must be None or str` names that case.
    if optional and _is_absent(value):
        return None
    raw = _faithful(value)
    if isinstance(raw, (bytes, bytearray, memoryview)):
        return raw
    raise MIRRORS["TypeError"](
        f"#{selector} expects bytes, got {article(type(value).__name__)}"
    )


def a_block(
    value: Any, selector: str, role: str = "a block", param: str = "item"
) -> Any:
    """`value`, or a refusal naming the message and the argument it wanted.

    `_require_block`'s call-site twin for the ~40 messages that take a block and
    reached the deferred call instead. Its docstring already made the argument:
    "resolve what you need before running anything, so the failure lands where
    the mistake was written rather than after a deferred block has had side
    effects." Two proposals applied that to `Try` and `With`; nothing carried it
    to the collection protocol, where blocks are what POOP replaced every
    control structure *with*.

    Sending a non-block split three ways, and all three were wrong: seventeen
    messages leaked `'int' object is not callable` — true of every POOP object,
    and silent about what was expected; five **accepted in silence**, because
    `map`, `filter` and `filter_false` answer a view and call nothing until it
    is walked; and the `if_*` family reported or not depending on the
    *receiver's value*, so `True.if_true(5)` refused while `True.if_false(5)`
    said nothing. A program could ship a mistake that only reports on the branch
    it does not usually take.
    """
    if callable(value):
        return value
    # `lambda: …` for a zero-argument block, not `lambda : …` — the branch
    # family and the `if_none` pair take no parameter at all.
    spelt = f"lambda {param}: …" if param else "lambda: …"
    # `nothing` for an argument that was never passed. Without it, a missing
    # block fell through to CPython's call machinery, which builds its sentence
    # from the *function's* qualname — and the mixins are cloaked as `object`,
    # since no single builtin name is true for every wrapper that inherits
    # them. So `[1, 2].map()` blamed `object.map()`: a name a program can
    # write, for a class that does not answer `#map`, checkable in one line and
    # the opposite of what the refusal just said.
    got = "nothing" if value is MISSING else article(type(value).__name__)
    raise MIRRORS["TypeError"](
        f"#{selector} expects {role}, got {got} — write .{selector}({spelt})"
    )


def a_key(value: Any, selector: str) -> Any:
    """The optional `key` of `sorted` / `sort` / `min` / `max`, or a refusal.

    Absent by default, unlike every other block slot, so it cannot go through
    `a_block` — and it is the one that answered CPython's `'int' object is not
    callable` from inside the sort rather than at the call the reader wrote.

    Absence is the caller's to handle and is already handled there: `_minmax`
    and `_sorted` both omit the kwarg entirely rather than pass `key=None`,
    which matches no `min`/`max`/`sorted` overload. So this only ever sees a key
    the program actually wrote.
    """
    if callable(value):
        return value
    raise MIRRORS["TypeError"](
        f"#{selector}'s key must be a block, got {article(type(value).__name__)} — "
        f"write .{selector}(key=lambda item: …)"
    )


def byte_order(value: Any, selector: str) -> str:
    """`"big"` / `"little"`, or POOP's refusal.

    `to_bytes` and `from_bytes` handed the argument to CPython, which answered
    `to_bytes() argument 'byteorder' must be str, not int` — the message spelt
    as a call. The two valid spellings are named here rather than left to the
    conversion, so a typo (`"Big"`) is refused by the message that takes it.
    """
    # circular: _unwrap -> boolean -> _argument
    from poop.types._unwrap import _is_absent  # noqa: PLC0415

    if _is_absent(value):
        return "big"
    # Two failures, two classes, as CPython has them: a non-string is a
    # TypeError about the argument's kind, a misspelt one a ValueError about
    # its value. Only the sentences change.
    raw = text_like(value, selector, "a str", (str,))
    if raw in ("big", "little"):
        return raw
    raise MIRRORS["ValueError"](f"byte order must be 'big' or 'little', got {raw!r}")


def max_split(value: Any, selector: str) -> int:
    """The raw `maxsplit` of `split` / `rsplit`, or POOP's refusal.

    CPython answered `'str' object cannot be interpreted as an integer` — no
    message, no argument, and "interpreted as" naming a conversion the program
    never asked for. `a_bound` already words the same mistake for positions;
    an absent one is CPython's `-1`, every split there is.
    """
    return an_int(value, selector, "maxsplit", -1)


def an_int(value: Any, selector: str, role: str, default: Any = MISSING) -> Any:
    """The raw integer behind `value`, or POOP's refusal.

    `a_bound` for the integers that are not positions: a width, a length, a
    digit count, an index, a byte. CPython answered `'str' object cannot be
    interpreted as an integer` for all of them — the sentence `max_split`
    replaces, on 29 more receiver/message sites the wording sweep could not
    see, since it carries no call, no dunder and no operator.

    `default` is what an absent argument stands for. Without one the argument
    is mandatory, and `none` is refused like any other non-integer.
    """
    # circular: _unwrap -> boolean -> _argument
    from poop.types._unwrap import _is_absent  # noqa: PLC0415

    if default is not MISSING and _is_absent(value):
        return default
    raw = _faithful(value)
    if hasattr(raw, "__index__"):
        return raw
    raise MIRRORS["TypeError"](
        f"#{selector}'s {role} must be an int, got {article(type(value).__name__)}"
    )


def a_collection(value: Any, selector: str) -> Any:
    """`value` when it can be walked, else POOP's refusal.

    `zip`, the set algebra, `join`, `extend`, `update` and `fromkeys` take
    anything with elements, and a scalar reached CPython: `'int' object is not
    iterable`, on 33 receiver/message sites. "Iterable" is the protocol
    `no_iter` bans, and POOP has no such word — what it has is "a collection",
    the word a spread into a literal already refuses with.
    """
    if isinstance(value, Iterable):
        return value
    raise MIRRORS["TypeError"](
        f"#{selector} expects a collection, got {article(type(value).__name__)}"
    )


def a_pair(value: Any, selector: str) -> Any:
    """One entry of a collection of key/value pairs, or POOP's refusal.

    `d.update([1])` passes `a_collection` — it was handed one — and CPython
    then answered `object is not iterable` about the element, with no subject
    at all.
    """
    if isinstance(value, Iterable):
        return value
    raise MIRRORS["TypeError"](
        f"#{selector} expects key/value pairs, "
        f"got {article(type(value).__name__)} among them"
    )


def byte_source(value: Any, selector: str) -> Any:
    """What `from_bytes` reads its bytes from, or POOP's refusal.

    `bytes_like` for a message that also takes any iterable of ints, as
    `int.from_bytes([1, 2])` does. Anything else reached CPython, which
    answered `cannot convert 'int' object to bytes` — and a collection of the
    wrong things answered about an element, in the same words `max_split`
    replaces.
    """
    raw = _faithful(value)
    # An int is asked first: `bytes(5)` is five zero bytes, not a refusal.
    if not hasattr(raw, "__index__"):
        try:
            return bytes(raw)
        except TypeError:
            pass
    return bytes_like(value, selector)


def _opt_stop(bound: Any, end: int) -> int:
    """`bound`, or the whole length when it was absent.

    `list.index` — unlike `str.index` — takes no `None` bound, so a missing
    `stop` becomes the receiver's length. `a_bound` has already unwrapped
    POOP's `none` to Python's `None` by the time this reads it.
    """
    return end if bound is None else bound
