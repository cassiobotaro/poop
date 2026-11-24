# 49. `raise_` is a class-side message, `raise_from` an instance one

Date: 2026-08-09

## Status

Accepted

## Context

`no_raise` forbids the `raise` statement and names `ExcType.raise_('msg')`. That spelling used to be a parse-time rewrite: `RaiseTransformer` matched a literal uppercase `ast.Name` followed by `.raise_(...)` and produced `_poop_raise(ExcType, ...)`. This had three effects.

- Only that spelling worked. `err = ValueError; err.raise_("boom")`, `d.at("e").raise_("boom")` and `e.kind().raise_(e.message())` all answered `ValueError does not understand #raise_`, untrue of the object, since nothing defined `raise_` anywhere. The third mattered most, because `Try` swallows an exception as soon as a handler matches and `raise` is banned, so there was no way to re-raise, or to raise a class a program computed.
- The substitute was invisible. `dir()` on an exception class did not list `raise_`, so `:methods` could not show what `no_raise` points at.
- Any capitalized receiver was assumed raisable. `class A(Object)` then `A.raise_("x")` answered `A() takes no arguments`, the constructor of a class the program never asked to build.

The rewrite also constrained `ExceptionTransformer` to run after `RaiseTransformer`: rewriting `ValueError` to `_poop_ValueError` first left a name starting with an underscore, and `raise_` then silently went unrecognised.

What the rewrite bought had to be kept. `raise_` is an expression, so it works inside a `lambda`, which was the reason for `_poop_raise`. `**kwargs` ride along. Since `raise` is a statement, `raise_` is the only way to signal an error, and an exception whose fields arrive by keyword must be raisable. The receiver parameter, though, took a keyword for itself: `Tagged.raise_(cls="x")` answered `Tagged.raise_() got multiple values for argument 'cls'`, a parameter the program never wrote (found by `ty` 0.0.106 in the `2026-11-22-bump-ty` change).

`no_raise` banned the `from` clause with the rest of the statement and nothing replaced it. A keyword on the class-side `raise_` (`KeyError.raise_("outer", from_=e)`) was the alternative and was rejected, because that message hands its keywords to the exception's own fields (`Field.raise_(code=7)`), and a cause keyword would take a name away from every program's exception class, besides reading poorly (`2026-10-19-complete-exception-protocol`).

## Decision

`raise_` is a `class_side` message on `PoopExcMeta` (`poop/types/exceptions.py`), not a parse-time rewrite.

- Every mirror, and every user class descending from one, answers it, and nothing else does. `PoopMeta` carries the refusing twin: `A cannot be raised — only a class descending from Exception can`. `PoopMeta.__dir__` lists `raise_` for the exception classes that answer it and no others.
- Its receiver is positional-only (`def raise_(cls, /, *args, **kwargs)`), on `PoopExcMeta` and on the refusing twin, so every keyword is the exception's, `cls` included.

`raise X from Y` is `X.raise_from(Y)`, sent to the built exception. It lives on the instance side of the root mirror, beside the instance `raise_`, and reads in Python's order: `KeyError("outer").raise_from(e)`. The cause is resolved before anything is raised.

- A caught `Error` stands for the exception it wraps.
- A built exception instance is used as it is.
- `None` is `raise … from None`, which drops the context.
- Anything else is refused: `#raise_from takes an exception or None, got an int`, `got the class ValueError`, `got nothing`, `got 2 arguments`. CPython would instantiate a class; a cause is something that happened, and a class has not.

There is no class-side `raise_from`, and no `raise_from` on a caught `Error`, which keeps refusing it through `does_not_understand`. The zero-argument `raise_` of a built exception and of a caught error count their arguments: `#raise_ takes no argument once the exception is built, got 1 argument` and `#raise_ takes no argument on a caught error, got 1 argument`.

## Consequences

The mirror answers `raise_` whatever it is called, so a program can re-raise (`e.kind().raise_(e.message())`) and raise a class it computed. The ordering constraint between `ExceptionTransformer` and `RaiseTransformer` is retired, since it existed only because the rewrite matched on the name's spelling.

The keyword channel belongs to the exception's fields alone: a field named `cls` arrives like any other, and no cause keyword competes with them.

Making `raise_` a message did not list it in `dir()` on its own, because `type.__dir__` never merged the metaclass's names; `PoopMeta.__dir__` is what lists it.
