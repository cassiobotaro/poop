# 12. Constructor builtins are intercepted, not banned

Date: 2026-04-22

## Status

Accepted

## Context

POOP has no free functions (ADR 6), and a call such as `len(x)` is replaced by a message (ADR 7). `int()`, `float()`, `bool()`, `str()`, `bytes()`, `list()`, `tuple()`, `set()`, `dict()` and the other type builtins are written the same way, but they are class constructors, which instantiate objects and fit the OO model. Called as Python spells them, they would still answer native values (ADR 3).

## Decision

Constructor builtins are intercepted, not banned. Each wrapper's transformer intercepts the bare call and rewrites it through a `_poop_X_from(...)` factory that answers the POOP type; for example, `str(...)` becomes `_poop_str_from(...)`, whatever the arity.

## Consequences

- A program converts values with the names it knows from Python, and gets a POOP value back.
- Each converter transformer also has to decide what a bare, uncalled builtin name means; that is ADR 51.
