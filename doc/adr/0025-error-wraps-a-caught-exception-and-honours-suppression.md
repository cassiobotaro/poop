# 25. `Error` wraps a caught exception and honours suppression

Date: 2026-04-23

## Status

Accepted

## Context

A `Try.except_` handler is given the exception it caught, and that object has to be a POOP object that answers messages.

`Error.__str__` used to print `Error(division by zero)`, naming a `poop.types` detail user code can neither name nor construct. The same object therefore identified itself two ways: `e.class_name()` answered `ZeroDivisionError` while `e.print()` answered `Error(...)`.

The `2026-10-19-complete-exception-protocol` change found that a caught error could not be asked for its cause, and that the uncaught report showed only the last exception although CPython already chains the one a handler was handling. A handler runs inside `Try._execute`'s `except`, so an exception it raises already carries the caught one as `__context__`. But every failure POOP composes is raised `from None` while CPython's native exception is still being handled (50 sites at the time, none `from exc`). That sets `__suppress_context__` and leaves `__context__` holding the native exception. Answering the raw `__context__` faithfully was rejected, because it would hand `e.context().message()` CPython's `list index out of range` behind POOP's `list has no element at 5 — it has 1 element`, for nearly every error the language words.

There were two more gaps. `PoopExcMeta.raise_` passes `**kwargs` to an exception whose fields arrive by keyword, and `Error` then hid them. `Field.raise_(code=7)` reached a handler whose `e.code` answered `Field does not understand #code`, with `has_attr`, `get_attr` and `dir` agreeing. And `Try` builds a fresh wrapper per handler, so the error `raise_` re-signalled compared unequal to the one first caught.

## Decision

`Error(Object)` (`poop/types/error.py`) wraps a caught Python exception, and handlers in `Try.except_` always receive an `Error`. It answers:

- `message()`, the exception message as a `Str`;
- `kind()`, the POOP exception class (`kind().name()` for its name as a `Str`);
- `cause()`, the error this one was raised from (`raise_from`), or `none`;
- `context()`, the error being handled when this one was raised, or `none` when there was none or it was suppressed.

`__str__` is built on the identity `class_()` answers (`"ZeroDivisionError: division by zero"`), not on the wrapper. A message-less exception prints as the bare class name, without a dangling colon, as `executor._describe` does.

`cause()` and `context()` answer an `Error`, the type a handler already holds. `context()` answers `none` when the context was suppressed: by POOP's own `from None`, by `raise_from(None)`, or by any explicit cause. The uncaught report follows the same rule, so a handler and the terminal never disagree.

`Error.does_not_understand` forwards a public name that the exception's own instance dictionary holds (the state a program's `__init__` wrote, filtered by `is_message` as `dir` filters everywhere) before refusing. The `BaseException` natives `args`, `add_note` and `with_traceback` are refused with the class side's own sentences. Equality and hash are the wrapped exception's identity, the shape `_MethodBlock` uses for a bound method.

## Consequences

- `message()`, `kind()` and `raise_()` carry over to the errors `cause()` and `context()` answer, and `e.cause() == earlier_e` holds.
- The error a handler re-raises is equal to the one it caught.
- A handler that raises inside a `Try` handler needs nothing new for the context; CPython sets it.
- `context()` deliberately diverges from the raw `__context__`. There is no `suppress_context()` to ask, because both `context()` and the report already honour it.
- `raise_from` on a caught `Error` is not offered; the error refuses it through `does_not_understand`. `Error.raise_` takes no argument and answers `#raise_ takes no argument on a caught error, got 1 argument`.
