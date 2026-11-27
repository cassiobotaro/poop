# with-type Specification

## Purpose
`With`, the construct replacing the `with` statement: how it is built and
run.

## Requirements

### Requirement: With counts its arguments in POOP's words
`With(...)` SHALL refuse no argument or more than one with a sentence naming
the construct and the block it takes, never `__init__` or `positional
argument`.

#### Scenario: No argument
- **WHEN** a program runs `With()`
- **THEN** a `TypeError` is raised reading `With takes one block, got nothing — write With(lambda: …)`

#### Scenario: Two arguments
- **WHEN** a program runs `With(lambda: 1, lambda: 2)`
- **THEN** a `TypeError` is raised reading `With takes one block, got 2 arguments — write With(lambda: …)`

### Requirement: With refuses a body that answers a coroutine
`With.do(body)` SHALL refuse a body that answers a coroutine, since the
coroutine would run after the manager has exited. The manager SHALL still
be exited, and the coroutine SHALL be closed, so no "never awaited" warning
follows the refusal.

#### Scenario: An awaiting body
- **WHEN** a program runs `With(lambda: cm).do(lambda r: obj.fetch())` with a manager that prints `exit`
- **THEN** it prints `exit` and a `TypeError` is raised reading `the With body answered a coroutine, which would run after the manager exits — use AsyncWith with an asynchronous context manager`

### Requirement: With names a body that answers a Try that has not run
When `With.do(body)`'s body answers a `Try` that has not run, the refusal
SHALL name it as a `Try` that has not run, not as a coroutine. The manager
SHALL still be exited.

#### Scenario: A body that forgets run
- **WHEN** a program runs `With(lambda: cm).do(lambda r: Try(lambda: 1))` with a manager that prints `exit`
- **THEN** it prints `exit` and a `TypeError` is raised reading `the With body answered a Try that has not run — send #run to it`
