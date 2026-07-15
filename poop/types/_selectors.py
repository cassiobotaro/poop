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


def explain(obj: object, name: str) -> str:
    """The `does not understand` message, with the best hint available.

    Three shapes, most specific first: the Smalltalk selector this receiver
    spells differently, a close match for a typo, or a pointer at `:methods`.
    """
    label = type(obj).__name__
    poop_name = SMALLTALK_SELECTORS.get(name)
    if poop_name is not None and hasattr(obj, poop_name):
        return (
            f"{label} does not understand #{name} — "
            f"Smalltalk's #{name} is #{poop_name} here"
        )
    known = [n for n in dir(obj) if not n.startswith("_")]
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
