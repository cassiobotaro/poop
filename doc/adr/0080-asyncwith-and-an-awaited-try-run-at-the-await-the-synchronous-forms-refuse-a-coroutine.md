# 80. AsyncWith and an awaited Try run at the await; the synchronous forms refuse a coroutine

Date: 2026-11-27

## Status

Accepted

Amends [26. `With` keeps the native protocol and passes POOP values; it checks both arguments where written](0026-with-keeps-the-native-protocol-and-passes-poop-values-it-checks-both-arguments-where-written.md)

Amends [54. `Try` answers values and `else_` receives the value; it checks both arguments where written](0054-try-answers-values-and-else-receives-the-value-it-checks-both-arguments-where-written.md)

## Context

`Try(block).run()` and `With(cm).do(body)` run their block at once. Inside an async method, a block cannot await (ADR 75), so a block that reaches asynchronous work only creates the coroutine. Run on CPython 3.15.2, a `ValueError` raised by an awaited coroutine escaped a `try` around the block that created it. The failure is raised at `.await_()`, after the `Try` is over, and the body of a `With` runs after its manager has exited.

Without a guard that covers an await, a program can catch an asynchronous failure only by wrapping the whole `Async.run`. `Async.timeout` fails a body with `TimeoutError` where the deadline fires, inside the async method.

The common handler answers a fallback value, as in `lambda e: "late"`. A handler that retries or fetches a fallback has to await.

`finally_` is terminal by ADR 54: it stores the cleanup and runs the `Try`.

## Decision

We will make the asynchronous forms run at the await. `AsyncWith(cm_block).do(body)` answers a coroutine. Awaiting it enters the manager through `__aenter__`, hands the body what entering answered, awaits the coroutine the body answers, and exits through `__aexit__`, which receives what `With`'s `__exit__` receives. A `Try` answers `.await_()`: awaiting it runs the block, awaits the coroutine the block answers inside the guard, and applies the handlers and `else_` as `run()` does.

We will require the coroutine where the asynchronous form exists for it. The body of an `AsyncWith` and the block of an awaited `Try` must answer one, and are refused otherwise, naming `With` and `run()`. A handler or `else_` of an awaited `Try` may answer a value or a coroutine, and a coroutine is awaited.

We will refuse a coroutine in the synchronous forms. `Try.run()`, `Try.finally_()` and `With.do()` refuse a block or body that answers one, close it, and name the asynchronous form. The refusal is raised outside the handlers, so a handler for `TypeError` does not swallow it.

## Consequences

A failure raised at an await is caught by a guard written around it, `TimeoutError` included.

An awaited `Try` has no cleanup clause, since `finally_` runs the `Try` when it is sent. An asynchronous cleanup is an `AsyncWith`.

A synchronous manager cannot guard an awaiting body, which Python allows as `with lock: await x`. A program gives its manager `__aenter__` and `__aexit__` instead.

The handlers and the body are checked asymmetrically on purpose. A block or a body that answers no coroutine where one is expected is almost certainly a mistake, while a handler that answers a constant is the usual case.

`Try` runs its guard in two places, one synchronous and one awaited, which share the handler match but not the control flow.
