"""Smalltalk selectors mapped to the POOP messages that answer them.

`difflib` measures *string* similarity, but Smalltalk → POOP is a *vocabulary*
mapping, so it only ever reaches the selectors whose spelling POOP happened to
keep. Measured against ten real selectors it scored three — `printNl`, `do:`
and `ifTrue:`, all three cases where both languages chose the same word — and
answered confidently wrong on the rest: `size` suggests `slice`, `inject:into:`
suggests `insert`, `notNil` suggests `not_`. No similarity cutoff fixes that;
there is no letter shared between `size` and `len`. The mapping has to be
written down.

Only selectors POOP spells differently are listed. `includes:`, `do:` and
`reversed` already answer under their own names, so they never reach here.
"""

import difflib
import inspect
from types import MemberDescriptorType

# Smalltalk drops its colons at POOP's call sites (`xs.collect(...)`), so the
# keys are what actually lands in `__getattr__`.
SMALLTALK_SELECTORS: dict[str, str] = {
    "asSortedCollection": "sorted",
    "collect": "map",
    "detect": "find",
    "displayNl": "print",
    "ifFalse": "if_false",
    "ifNil": "if_none",
    "ifNotNil": "if_not_none",
    "ifTrue": "if_true",
    "ifTrueIfFalse": "if_true_if_false",
    "inject": "reduce",
    "isNil": "is_none",
    "notNil": "not_none",
    "printNl": "print",
    "reject": "filter",
    "reverse": "reversed",
    "select": "filter",
    "size": "len",
}

# Names programmers bring from JavaScript, Java, Ruby and C#, keyed by the
# receiver's builtin name — the table Python 3.15 added to `AttributeError`
# (`traceback._CROSS_LANGUAGE_HINTS`), which is private to CPython and so
# copied rather than imported. Each row keeps CPython's hint where POOP has the
# same message, and translates it where CPython's names a construct POOP
# forbids: `contains` → `Use 'x in list'` is `no_in`'s ban, `put` → `Use d[k]
# = v` is `no_subscript`'s. The float rows (`__or__` and its siblings) are
# left out — a dunder never reaches the hook. The receiver is matched through
# its MRO, as CPython's `isinstance` does, so a program's `class Stack(list)`
# gets the list rows.
CROSS_LANGUAGE_HINTS: dict[tuple[str, str], str] = {
    # list — JavaScript/Ruby, then Java/C#
    ("list", "push"): "did you mean #append?",
    ("list", "concat"): "did you mean #extend?",
    ("list", "addAll"): "did you mean #extend?",
    ("list", "contains"): "did you mean #includes?",
    ("list", "add"): "did you mean to use a set?",
    # str — JavaScript
    ("str", "toUpperCase"): "did you mean #upper?",
    ("str", "toLowerCase"): "did you mean #lower?",
    ("str", "trimStart"): "did you mean #lstrip?",
    ("str", "trimEnd"): "did you mean #rstrip?",
    # dict — Java/JavaScript
    ("dict", "keySet"): "did you mean #keys?",
    ("dict", "entrySet"): "did you mean #items?",
    ("dict", "entries"): "did you mean #items?",
    ("dict", "putAll"): "did you mean #update?",
    ("dict", "put"): "did you mean #at_put?",
    # tuple — a mutable message on an immutable receiver
    ("tuple", "append"): "did you mean to use a list?",
    ("tuple", "extend"): "did you mean to use a list?",
    ("tuple", "insert"): "did you mean to use a list?",
    ("tuple", "remove"): "did you mean to use a list?",
    # frozenset — the same, one type over
    ("frozenset", "add"): "did you mean to use a set?",
    ("frozenset", "remove"): "did you mean to use a set?",
    ("frozenset", "discard"): "did you mean to use a set?",
    ("frozenset", "update"): "did you mean to use a set?",
}


def is_message(name: str) -> bool:
    """A name user code may send — the predicate `Object.dir()` uses.

    Every `_`-prefixed name is hidden: dunders (`no_dunder_attribute` bans
    them), the mangled `_poop_*` bindings, and the single-underscore internals
    `_reject_private` refuses at runtime. Four surfaces answer the same
    question — `dir()`, `:methods`, the near-miss hint below, and the REPL's
    tab-completion — and three of them had their own copy of the rule. The
    fourth, the completer, spelt it `not name.startswith("__")` and so offered
    `x._value`, the raw Python value behind the wrapper, as a completion: the
    encapsulation leak taught by the tool meant to teach the language.
    """
    return not name.startswith("_")


def is_dunder(name: str) -> bool:
    """`__name__`-shaped — Python's protocol, never POOP's message surface.

    The one copy of the test the dunder ban, the private ban and the two
    `__getattr__` hooks all ask. It was spelt inline at each of them.
    """
    return name.startswith("__") and name.endswith("__")


def receiver_label(obj: object) -> str:
    """How a receiver names itself in a message about it.

    A class answers its own name — `type(cls)` says `PoopMeta`, an internal no
    program can write. Shared with `:methods`, whose header read `PoopExcMeta
    understands 30 messages` for `ValueError`.
    """
    return obj.__name__ if isinstance(obj, type) else type(obj).__name__


def not_understood(label: str, name: str, hint: str) -> str:
    """`<label> does not understand #<name> — <hint>`, the refusal's one shape."""
    return f"{label} does not understand #{name} — {hint}"


def explain(obj: object, name: str, label: str | None = None) -> str:
    """The `does not understand` message, with the best hint available.

    Three shapes, most specific first: the Smalltalk selector this receiver
    spells differently, a close match for a typo, or a pointer at `:methods`.

    `label` overrides how the receiver names itself. Only `Error` passes it:
    the wrapper is cloaked as `object` because no exception name is true for
    the *class*, while an instance stands for exactly one and already answers
    its name through `class_()`, `class_name()` and `__str__`. Deriving it
    here instead would mean asking every receiver for its class, which is a
    message a proxy is free to answer with anything.
    """
    if label is None:
        label = receiver_label(obj)
    poop_name = SMALLTALK_SELECTORS.get(name)
    if poop_name is not None and hasattr(obj, poop_name):
        return not_understood(label, name, f"Smalltalk's #{name} is #{poop_name} here")
    foreign = _cross_language_hint(obj, name)
    if foreign is not None:
        return not_understood(label, name, foreign)
    known = [n for n in dir(obj) if is_message(n)]
    # 0.7, not difflib's default 0.6. With the tables above carrying the
    # Smalltalk and the foreign vocabularies, all that is left here is typos,
    # and those score high: measured over six real ones and four nonsense
    # names, 0.6 caught 6/6 but invented `frobnicate` → `from_bytes` and
    # `blerg` → `clear`, while 0.7 caught 5/6 and invented nothing. Losing
    # `lenght` → `len` is cheaper than confidently naming a message the user
    # never meant.
    matches = difflib.get_close_matches(name, known, n=1, cutoff=0.7)
    if matches:
        return not_understood(label, name, f"did you mean #{matches[0]}?")
    nested = _nested_hint(obj, name, known)
    if nested is not None:
        return not_understood(label, name, f"did you mean #{nested}?")
    return not_understood(label, name, "try :methods to list its messages")


def _cross_language_hint(obj: object, name: str) -> str | None:
    """The row of `CROSS_LANGUAGE_HINTS` for this receiver, if any."""
    mro = obj.__mro__ if isinstance(obj, type) else type(obj).__mro__
    for cls in mro:
        hint = CROSS_LANGUAGE_HINTS.get((cls.__name__, name))
        if hint is not None:
            return hint
    return None


def _nested_hint(obj: object, name: str, attrs: list[str]) -> str | None:
    """`inner.name` when one of the receiver's attributes answers `name`.

    Python 3.15's nested-attribute hint (`Did you mean '.inner.area' instead
    of '.area'?`), one level deep and over at most twenty attributes, as
    CPython bounds it. Nothing runs: an attribute that is a descriptor on the
    class — a method, a property — is skipped, and the inner object is asked
    statically, so no `__getattr__` and no `does_not_understand` fires while
    composing a hint about another one. The REPL's completer uses the same
    `getattr_static` for the same reason.
    """
    for attr in attrs[:20]:
        on_class = inspect.getattr_static(type(obj), attr, None)
        # A `__slots__` member is a descriptor too, but reading it runs
        # nothing — and every POOP class declares its state that way, so
        # skipping it would skip every receiver the hint exists for.
        if hasattr(on_class, "__get__") and not isinstance(
            on_class, MemberDescriptorType
        ):
            continue
        # Safe to read now: a plain attribute or a slot runs no code. The
        # inner object is still asked statically, so its own hook stays quiet.
        inner = getattr(obj, attr, None)
        if inner is not None and inspect.getattr_static(inner, name, None) is not None:
            return f"{attr}.{name}"
    return None
