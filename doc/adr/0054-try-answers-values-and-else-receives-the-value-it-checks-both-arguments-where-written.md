# 54. `Try` answers values and `else_` receives the value; it checks both arguments where written

Date: 2026-08-11

## Status

Accepted

## Context

`no_try` bans the `try` statement, and `Try` (`poop/types/try_.py`) is its substitute: a message-passing builder for try/except/else/finally whose block runs lazily, only when `.run()` or `.finally_()` is sent. Without a value from those messages, `try: return f() except: return default` is not expressible, and `no_try` would ban a construct with no substitute.

`no_try` banned `try … else` with the rest of the statement while `Try` answered `else_` with `Try does not understand #else_`, a ban without a substitute. In Python the `try` assigns a name and the `else` reads it; a lambda cannot assign.

The arguments were checked late or not at all.

- `except_` left the exception kind to `isinstance` inside `_execute`, so a quoted class name answered `isinstance() arg 2 must be a type, a tuple of types, or a union`, the banned builtin spelt as the call replacing it. It answered only when the protected block happened to raise; the same mistake said nothing otherwise, and saying nothing means the handler was never installed.
- Bound as a class rather than through a converter, `Try()` and `Try(a, b)` reached CPython's call machinery and answered `Try.__init__() missing 1 required positional argument: 'block'`, a dunder and a phrase the wording sweep bans, from one of the two names a program is invited to spell.

## Decision

`.run()` and `.finally_()` answer the protected block's value, or the matching handler's value when one fires, like every other POOP block and like Smalltalk's `on:do:`. Both are terminal; `.except_()` is the chainable message. The cleanup block's own value is discarded, mirroring Smalltalk's `ensure:`. Multiple `.except_()` calls are matched in order, and unhandled exceptions are always re-raised.

`else_` is Python's `else` clause, and it hands the value on: the block receives the protected block's value, and its own value is what `run()` and `finally_()` answer. `Try(lambda: int("21")).except_(ValueError, lambda e: -1).else_(lambda n: n * 2).run()` is `42`, and `-1` for `"x"`. The implementation is Python's `else` branch, so a handler never catches what the `else_` block raises, and the cleanup runs after it either way. One `else_` per `Try`, as Python allows one `else`: a second answers `Try already has an else clause — send #else_ once`.

`Try` checks each argument where it was written.

- `except_` routes the kind through `_argument.a_class`, unwraps a POOP `Tuple` so Python's "catch either" spelling works, and refuses a class that is no exception (`#except_ catches exception classes, and int is not one`), as CPython refuses `except int`. The kind is a POOP exception class (ADR 34).
- `else_` refuses a non-block: `the else clause must be a block, got an int — write .else_(lambda value: …)`.
- The constructor takes `block` positionally with a sentinel default and counts the rest, in the converters' phrasing: `Try takes one block, got nothing — write Try(lambda: …)`, and `got 2 arguments` for the other shape.

`Try` is exposed in `DEFAULT_NAMESPACE` through the `NAMESPACE` dict in `poop/transformers/try_.py`, with no AST rewrite.

## Consequences

`try … else` has a substitute, so `no_try` no longer bans it without one.

A wrong kind is refused when the handler is installed, whether or not the protected block raises.

A block of the wrong arity is still reported when it is called, as every handler's is; arity is not checked where the block is written.

`With` checks its arguments by the same rule (ADR 26).
