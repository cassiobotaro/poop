# Spec Delta

## Purpose
`AsyncWith`, the construct replacing `async with`: how it is built, what
awaiting it runs and in what order, and what it refuses.

## ADDED Requirements

### Requirement: AsyncWith counts its arguments in POOP's words
`AsyncWith(...)` SHALL refuse no argument or more than one with a sentence
naming the construct and the block it takes.

#### Scenario: No argument
- **WHEN** a program runs `AsyncWith()`
- **THEN** a `TypeError` is raised reading `AsyncWith takes one block, got nothing — write AsyncWith(lambda: …)`

#### Scenario: Two arguments
- **WHEN** a program runs `AsyncWith(lambda: 1, lambda: 2)`
- **THEN** a `TypeError` is raised reading `AsyncWith takes one block, got 2 arguments — write AsyncWith(lambda: …)`

### Requirement: Awaiting AsyncWith runs the body inside the manager
`AsyncWith(cm_block).do(body)` SHALL answer a coroutine and run nothing.
Awaiting it SHALL enter the manager, hand the body what entering answered,
await the body's coroutine, exit the manager, and answer the body's value.
A failure while the body's coroutine is awaited SHALL reach the manager's
exit, which receives the mirror class, an `Error` and `none`, as `With`'s
does.

#### Scenario: Nothing runs before the await
- **WHEN** a program sends `do` to an `AsyncWith` whose manager prints `enter` and does not await the answer
- **THEN** nothing is printed

#### Scenario: Order
- **WHEN** a manager prints `enter` and `exit`, the body's coroutine prints `body` and answers `1`, and an async method prints the awaited `AsyncWith`
- **THEN** it prints `enter`, `body`, `exit` and `1`, in that order

#### Scenario: A failure reaches the exit
- **WHEN** the body's coroutine raises `ValueError("x")` and the manager's exit prints `kind.name()`
- **THEN** it prints `ValueError` and the failure propagates

### Requirement: AsyncWith refuses what it cannot run
`AsyncWith` SHALL refuse a manager without the asynchronous protocol before
entering it, a body that is not a block, a body that answers no coroutine,
and a second `do`.

#### Scenario: A manager without the protocol
- **WHEN** an async method awaits `AsyncWith(lambda: 5).do(lambda r: obj.m())`
- **THEN** a `TypeError` is raised reading `int does not support the asynchronous context manager protocol — it cannot be entered`

#### Scenario: A body that does not await
- **WHEN** an async method awaits `AsyncWith(lambda: cm).do(lambda r: 1)`
- **THEN** a `TypeError` is raised reading `the AsyncWith body must answer a coroutine, got an int — use With for a body that does not await`, and the manager is exited

#### Scenario: Running twice
- **WHEN** a program sends `do` twice to the same `AsyncWith`
- **THEN** a `RuntimeError` is raised reading `AsyncWith has already run; create a new AsyncWith instance to run again.`
