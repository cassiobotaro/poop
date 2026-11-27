# 76. An async method answers a coroutine wrapped where the class is built

Date: 2026-11-27

## Status

Accepted

## Context

Sending an async method runs none of its body. CPython answers a coroutine object, and the body runs when that object is awaited. A program holds the coroutine between the send and the await, so it is a value the program can send messages to.

A raw coroutine answers none of POOP's messages. `obj.fetch().print()` fails with CPython's `'coroutine' object has no attribute 'print'`, and `does_not_understand` (ADR 36) never runs, since a coroutine does not descend from `Object`. ADR 4 calls a native value handed back to a program a bug. ADR 41 closed the same kind of leak for a method read off an object, which used to answer CPython's bound method.

A raw coroutine also exposes `cr_frame`, `cr_code`, `send` and `throw`. No name among them starts with an underscore, so ADR 15's rule does not reach them. No other value a program can hold today carries a frame: generators are refused, and a handler receives `none` for the traceback (ADR 26).

`asyncio.run`, `asyncio.gather` and `await` accept any object that defines `__await__`. That was run on CPython 3.15.2.

ADR 41 measured a wrapper placed on every attribute read at +81% on 200k sends.

## Decision

We will answer a `Coroutine` from every async method of a POOP class: a POOP value cloaked as `coroutine` that holds the raw coroutine and defines `__await__` and nothing else of the coroutine protocol. It prints as `<coroutine>`, the shape of `<block>`.

We will wrap where the class is built. `PoopMeta.__new__` asks `inspect.iscoroutinefunction` once for each entry of the class body, dunders included, and replaces each coroutine function with a synchronous one that answers `Coroutine(fn(...))`. The `message` descriptor then wraps that function as it wraps any other.

## Consequences

A send to a method that is not async costs what it cost before.

Every way of reaching an async method answers a `Coroutine`: a send, `super().m()`, `get_attr`, and an `async def __call__`. The last two never pass through a `message` descriptor, which is why the wrap is not placed there.

A coroutine is awaited once. A second await fails with CPython's `cannot reuse already awaited coroutine`, matched by the `RuntimeError` mirror (ADR 35).

CPython cannot emit its own "never awaited" warning for a program's coroutine. The warning imports through the builtins of the frame the coroutine is collected in, a program's builtins hold no `__import__` (ADR 40), and CPython prints `KeyError: '__import__'` in its place. The `Coroutine` emits the same warning when it is collected unawaited, from library code, at the line of the method's `def`, and closes the raw coroutine so CPython does not try.

The `Coroutine` makes a forgotten await harder to see. `obj.fetch().print()` prints `<coroutine>` where the raw value would have failed, and the warning is the only signal left.
