# 52. Native-demanding protocol slots are adapted at class build

Date: 2026-08-10

## Status

Accepted

## Context

`class P(Object)` may define dunders: `__init__`, `__eq__`, `__lt__`, `__enter__` and `__add__` all work, and contributors are told to wire dunders to public Python-named methods. A POOP method can only return POOP values, though, and CPython reads five of those slots itself and demands a native answer. Every one of the five was therefore unsatisfiable from inside the language, with a sentence that contradicted itself, because `_cloak` renamed the wrapper to the builtin it stands for:

- `__str__ returned non-string (type str)`;
- `__bool__ should return bool, returned bool`;
- a `__hash__` refusal that printed `__poop__.P`, the module marker `_reject_builtin` uses to tell a user's class from a builtin, which no program should ever see.

`__len__` was the quiet member of the family: defining it raised nothing and did nothing, because `len` is how POOP asks and nothing supplied it.

The wrappers in `poop/types/` answer these slots with natives already, and the package runs `bool(x)` during its own import.

## Decision

`PoopMeta.__new__` adapts `__str__`, `__repr__`, `__bool__`, `__hash__` and `__len__` where the class is built, unwrapping the answer through `_bridge.to_python`. A native answer short-circuits.

A wrong answer is refused by the role rather than the slot: `P's text must be a str, got an int`. A message spelling `__str__` would name the construct `no_dunder_attribute` bans.

A class that declares `__len__` and no `len` also answers the `len` message.

## Consequences

A program's class can satisfy every protocol slot it is allowed to define, with POOP values.

The short-circuit on a native answer is what keeps the wrappers in `poop/types/` untouched and the module importable.
