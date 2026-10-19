# Design

## Context

See proposal.md for the motivation. The facts that shape the approach:

- `Try._execute` (`poop/types/try_.py`) is a single Python
  `try/except BaseException/finally`. Handlers run inside the `except`, so
  an exception a handler raises already carries the caught one as
  `__context__`, set by CPython. Nothing reads it today.
- Every failure POOP composes inside `poop/types/` is raised
  `from None` (50 sites, none `from exc`), while CPython's native exception
  is still being handled. `__suppress_context__` is set, but `__context__`
  still holds the native exception and its wording.
- The class-side `raise_` (`PoopExcMeta.raise_`) passes its `**kwargs` to
  the exception's constructor, where a program's own fields arrive. The
  instance side (a built exception) and `Error` each answer a zero-argument
  `raise_()`.
- The CLI and the REPL both print a run-time failure through
  `poop/errors.py` (`format_error` / `render_error` / `report`), from an
  `ExecutionError` that carries a message and a line number only.
- `:explain try` runs the snippet in `_EXPLAIN_SNIPPETS` (`poop/repl.py`)
  through the validators and shows what they report; the snippet holds one
  `try/except`, so it reaches only the `ast.Try` sentence. The test that
  every validator message is explained reads only `self.report("…")`
  literals, not a `NodeValidator.messages` table, so it does not enforce
  the `except*` sentence; the snippet is extended for the reader, not the
  test.
- `1 / 0` raises CPython's own `ZeroDivisionError`; no wrapper rewords it.
  Its text, `division by zero`, is already the first line of today's report
  when it escapes alone, and will be a chain line's text too.
- The exception mirrors are not sampled by the wording sweep
  (`tests/test_no_python_wording.py`): a program meets them only as the
  `Error` that *is* sampled. Refusals on a built exception are pinned as
  programs in its `_FAILING` list.

## Goals / Non-Goals

**Goals:**
- One rule for which chain links are visible, shared by `context()` and
  the report, so a handler and the terminal never disagree.
- No new route by which CPython's wording reaches a program.

**Non-Goals:**
- `raise_from` on a caught `Error` (`e.raise_from(x)`, which would be
  `raise e from x`). It is not needed to express `raise X from Y`, and the
  error keeps refusing it through `does_not_understand`.
- A traceback per link. Only the final exception has a source line, as
  today.

## Decisions

### `raise_from` is an instance message, not a keyword on `raise_`

`KeyError("outer").raise_from(e)` reads in the order of `raise X from Y`.
The alternative, `KeyError.raise_("outer", from_=e)`, would take the name
`from_` away from the keyword channel that carries a program's own exception
fields, and `from_` reads poorly. The cause is resolved before anything is
raised:
- a caught `Error` becomes the exception it wraps;
- a built exception instance is used as it is;
- `None`, which a program writes and POOP rewrites to its `none`, becomes
  Python's `None`;
- anything else, including an exception class (which CPython would
  instantiate), is refused with `#raise_from takes an exception or None, got
  …`, worded through `describe_operand`.

The message lives on the instance side of the root mirror, beside the
instance `raise_`.

### `cause()` and `context()` answer an `Error` or `none`

Both wrap the linked exception in `Error`, the type a handler already
receives. That means `message()`, `kind()`, `raise_()` and equality by
identity of the wrapped exception all carry over, and
`e.cause() == earlier_e` holds. `context()` answers `none` when
`__suppress_context__` is set. The faithful alternative, answering the raw
`__context__`, was rejected: because of the 50 `from None` sites, it would
hand back CPython's native exception (`list index out of range`) for almost
every error POOP composes. With this rule, `suppress_context()` has nothing
left to answer, which is why it is not offered.

### One chain walk, used by the report

A single helper, beside `describe` in `poop/types/exceptions.py`, yields the
visible links of an exception. At each step it takes `__cause__` when that
is set, and otherwise `__context__` unless it is suppressed. It stops at
`None`, and it stops at an exception it has already seen, since a handler
can build a cycle. Each link is labelled `caused by` or `while handling` and
worded by `describe`, so the kind is the one a program can write. The
executor attaches those lines to `ExecutionError`, and `format_error` /
`render_error` print them after the quoted source line, indented two spaces
(a run-time failure carries no column, so there is no caret). The CLI and
the REPL get the chain from the same change. The `RecursionError` path keeps
its own message and walks the chain the same way.

The order is the reverse of CPython's (final exception first) because the
report opens with `poop: <Kind>: <message>` and the source line belongs to
that exception.

### `else_` is Python's own `else` clause

`_execute` gains an `else:` branch on its existing `try`. It calls the
stored block with the protected value and replaces `result`. Python places
it outside the handlers and before `finally`, which is exactly the required
ordering, with no bookkeeping. The block goes in a new `_else_block` slot,
released in the `finally` with the others.

`else_` follows `except_`:
- the block is checked with `_require_block` (role `the else clause`, hint
  `write .else_(lambda value: …)`);
- once the `Try` has executed, it stores nothing.

A second `else_` is refused (`Try already has an else clause — send #else_
once`) instead of replacing the first, because Python allows one
`else` and silently dropping a block is the failure `_require_block` exists
to prevent. Arity is not checked at the boundary: no block argument in POOP
is, and a wrong one answers `block expects 0 arguments, got 1` when called,
as a handler's does.

### `raise_` and `raise_from` count their arguments

Both zero-argument `raise_` methods take `*extra` and refuse a non-empty
one, counted by `_count`, the way `Try.__init__` counts; `raise_from` counts
the same way for more than one argument (`got 2 arguments`) and answers
`got nothing` for none. Once `Error.raise_` takes `*extra`, the sweep sends
it a wrong-typed argument on its own, since `Error` is sampled:
- `#raise_ takes no argument once the exception is built, got 1 argument`
  on the instance side;
- `#raise_ takes no argument on a caught error, got 1 argument` on `Error`.

### `except*` is a definitive ban

`no_try` keeps its `ast.Try` sentence and answers `ast.TryStar` with
`try/except* is forbidden — nothing in POOP raises an exception group`.
`INFECTIONS.md` adds it to the definitive-ban list in *Principles* and
explains it under *No `try`*: groups come from `asyncio.TaskGroup` and
concurrency, none of which POOP has. The `:explain try` snippet gains an
`except*` statement so a reader who types `:explain try` sees both
sentences.

## Risks / Trade-offs

- [A link is a native exception that escaped un-reworded, so the report
  shows CPython's wording on a `while handling` line] → The same text would
  already be the top line if that exception escaped alone. The new
  `[1].at(5)` CLI scenario and an entry in `test_no_python_wording` pin the
  common path.
- [Tests that compare the whole of stderr for a failure raised inside a
  handler change] → They gain a line. Grep `tests/` for handler-raised
  failures while doing the report task and update them in the same commit.
- [`context()` diverges from the raw dunder] → This is documented under
  *Error* in `INFECTIONS.md`, with the `from None` reason, so it is not
  "fixed" back later.
- [A handler builds a cycle (`a` raised from `b`, `b` from `a`)] → The walk
  stops at an exception it has already seen.
