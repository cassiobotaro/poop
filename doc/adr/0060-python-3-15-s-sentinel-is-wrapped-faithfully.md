# 60. Python 3.15's `sentinel` is wrapped faithfully

Date: 2026-10-09

## Status

Accepted

## Context

Python 3.15 made `sentinel` (PEP 661) a builtin. Refusing it was considered, since `MISSING = Object()` already works in POOP, and `sentinel(...)` looks like a free function. But the rule is to follow CPython, and CPython made it a builtin.

Two halves of the PEP have no surface in POOP: `copy`/pickle preserving identity, since neither exists here, and `|` building a type union (`int | MISSING`), which belongs to annotations POOP programs do not write.

Separately, the interpreter's own "argument not given" markers in `_sentinel.py` were an `Enum` imitating what the builtin gives natively (identity, narrowing in `ty`, a named repr), with one `Literal` type alias per member. The `2026-10-22-adopt-315-idioms` change verified that `ty` narrows a PEP 661 sentinel on `is`, but not when it is declared `MISSING: Final = sentinel(...)`: the `Final` annotation hides the sentinel type. Keeping a `type Missing = ...` alias of the sentinel was rejected as one more spelling of the same thing.

## Decision

`sentinel` is wrapped, not refused. `Sentinel` (`poop/types/sentinel.py`) answers what CPython answers:

- Every `sentinel("MISSING")` is a *new* object: `sentinel("M") is sentinel("M")` is false in 3.15, and so are `==` and an equal hash. Identity is the one thing a sentinel has, and `is_identical` is the question it exists for.
- Its `repr` is the name or the `repr` keyword; it is truthy; it answers no message of its own beyond `Object`'s.
- The converter keeps CPython's signature `(name, /, *, repr=None)`, the keyword spelt `repr` because that is what a program writes, and leaves the arity shapes to CPython under the cloaked name, as every converter does. The two type refusals are POOP's (`sentinel's name must be a str, got an int`).
- A `Sentinel` declines `|` like any other operand; copy and pickle are left out.

The internal `_sentinel.py` is built on the same builtin and takes the half the language's surface declines: `|` in the interpreter's own annotations. Markers are declared bare (`MISSING = sentinel("MISSING")`, no `Final`), and the annotation is the marker itself: `block: Block | MISSING = MISSING`, which `ty` narrows so the branch after `if block is MISSING` sees a `Block`.

## Consequences

The `Enum` and its five `Literal` aliases are gone; one name per marker. The markers' repr changes from `<missing>` to `MISSING`, which no user-facing message carries. A regression in `ty`'s sentinel support would show in `uv run ty check`.

`sentinel` can be subclassed in POOP where CPython refuses it (`type 'sentinel' is not an acceptable base type`): `_AliasMeta.__new__` refuses only the payload-less bases, and a `Sentinel` carries its name. This is recorded rather than closed: nothing relies on either answer, and a program that subclasses it gets a working sentinel.
