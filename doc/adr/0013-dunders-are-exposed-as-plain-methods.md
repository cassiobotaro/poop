# 13. Dunders are exposed as plain methods

Date: 2026-04-22

## Status

Accepted

## Context

POOP replaces free functions and operators with messages (ADR 7): `len(x)` becomes `x.len()`, `abs(x)` becomes `x.abs()`. The behaviour behind those builtins already lives on each type as a Python dunder (`__len__`, `__abs__`, `__hash__`). A message has to exist under a name the program can send, and that name could follow Python or Smalltalk.

## Decision

Every relevant dunder on a POOP type gets an alias under the Python name without the underscores: `__len__` is answered as `len()`, `__abs__` as `abs()`, `__hash__` as `hash()`, and so on. The alias is not translated to a Smalltalk name, by the naming rule of ADR 8.

## Consequences

The substitutes for builtins such as `len`, `abs` and `hash` carry the names a Python reader already knows. The dunder itself stays on the type, because CPython's protocols call it, and it keeps answering a native value where Python requires one; the named alias answers a POOP type, as ADR 4 requires.
