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


def is_message(name: str) -> bool:
    """A name user code may send — the predicate `Object.dir()` uses.

    Every `_`-prefixed name is hidden: dunders (`no_dunder_attribute` bans
    them), the mangled `_poop_*` bindings, and the single-underscore internals
    `Object._reject_private` refuses at runtime. Four surfaces answer the same
    question — `dir()`, `:methods`, the near-miss hint below, and the REPL's
    tab-completion — and three of them had their own copy of the rule. The
    fourth, the completer, spelt it `not name.startswith("__")` and so offered
    `x._value`, the raw Python value behind the wrapper, as a completion: the
    encapsulation leak taught by the tool meant to teach the language.
    """
    return not name.startswith("_")


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
    # A class answers its own name; `type(cls)` would say "PoopMeta".
    if label is None:
        label = obj.__name__ if isinstance(obj, type) else type(obj).__name__
    poop_name = SMALLTALK_SELECTORS.get(name)
    if poop_name is not None and hasattr(obj, poop_name):
        return (
            f"{label} does not understand #{name} — "
            f"Smalltalk's #{name} is #{poop_name} here"
        )
    known = [n for n in dir(obj) if is_message(n)]
    # 0.7, not difflib's default 0.6. With the table above carrying the
    # Smalltalk vocabulary, all that is left here is typos, and those score
    # high: measured over six real ones and four nonsense names, 0.6 caught
    # 6/6 but invented `frobnicate` → `from_bytes` and `blerg` → `clear`,
    # while 0.7 caught 5/6 and invented nothing. Losing `lenght` → `len` is
    # cheaper than confidently naming a message the user never meant.
    matches = difflib.get_close_matches(name, known, n=1, cutoff=0.7)
    if matches:
        return f"{label} does not understand #{name} — did you mean #{matches[0]}?"
    return f"{label} does not understand #{name} — try :methods to list its messages"
