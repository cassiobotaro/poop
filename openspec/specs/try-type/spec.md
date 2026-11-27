# try-type Specification

## Purpose
`Try`, the construct replacing `try`/`except`/`finally`: how it is built,
chained and run.

## Requirements

### Requirement: Try counts its arguments in POOP's words
`Try(...)` SHALL refuse no argument or more than one with a sentence naming
the construct and the block it takes, never `__init__` or `positional
argument`.

#### Scenario: No argument
- **WHEN** a program runs `Try()`
- **THEN** a `TypeError` is raised reading `Try takes one block, got nothing — write Try(lambda: …)`

#### Scenario: Two arguments
- **WHEN** a program runs `Try(lambda: 1, lambda: 2)`
- **THEN** a `TypeError` is raised reading `Try takes one block, got 2 arguments — write Try(lambda: …)`

### Requirement: else_ runs on success and answers in its place
`Try` SHALL answer `else_(block)`, chainable like `except_`. When the
protected block raises nothing, the block SHALL be called with the
protected block's value, and its own value SHALL be what `run()` or
`finally_()` answers. When the protected block raises, the block SHALL not
run.

#### Scenario: The protected block succeeds
- **WHEN** a program prints `Try(lambda: int("21")).except_(ValueError, lambda e: -1).else_(lambda n: n * 2).run()`
- **THEN** it prints `42`

#### Scenario: The protected block raises
- **WHEN** a program prints `Try(lambda: int("x")).except_(ValueError, lambda e: -1).else_(lambda n: n * 2).run()`
- **THEN** it prints `-1`

#### Scenario: Through finally_
- **WHEN** a program prints `Try(lambda: 1).else_(lambda n: n + 1).finally_(lambda: "done".print())`
- **THEN** it prints `done` and then `2`

### Requirement: else_ is outside the handlers and before the cleanup
An exception raised by the `else_` block SHALL not be caught by any handler
registered with `except_` on the same `Try`, and the cleanup given to
`finally_` SHALL run after the `else_` block, whether it raised or not.

#### Scenario: A handler does not catch the else block
- **WHEN** a program runs `Try(lambda: 1).except_(ValueError, lambda e: "caught".print()).else_(lambda n: ValueError.raise_("late")).run()`
- **THEN** `caught` is not printed and the program fails with `ValueError: late`

#### Scenario: The cleanup runs after a failing else block
- **WHEN** a program runs `Try(lambda: 1).else_(lambda n: ValueError.raise_("late")).finally_(lambda: "cleanup".print())`
- **THEN** it prints `cleanup` and then fails with `ValueError: late`

### Requirement: else_ refuses a non-block and a second else
`else_` SHALL refuse an argument that is not a block where it was written,
and SHALL refuse being sent twice to one `Try`. A block of the wrong arity
SHALL be reported when it is called, in the words every block uses.

#### Scenario: Not a block
- **WHEN** a program runs `Try(lambda: 1).else_(5)`
- **THEN** a `TypeError` is raised reading `the else clause must be a block, got an int — write .else_(lambda value: …)`

#### Scenario: A second else
- **WHEN** a program runs `Try(lambda: 1).else_(lambda n: n).else_(lambda n: n)`
- **THEN** a `TypeError` is raised reading `Try already has an else clause — send #else_ once`

#### Scenario: A block that takes nothing
- **WHEN** a program runs `Try(lambda: 1).else_(lambda: 2).run()`
- **THEN** a `TypeError` is raised reading `block expects 0 arguments, got 1`

### Requirement: An awaited Try guards a coroutine
`Try(block)` with its `except_` and `else_` clauses SHALL answer
`.await_()` inside an async method: it SHALL run the block, await the
coroutine it answers inside the guard, and apply the handlers and the
`else_` clause as `run()` does. A handler or `else_` answering a coroutine
SHALL have it awaited, and its value answered in its place.

#### Scenario: A failure at the await is caught
- **WHEN** `fetch` raises `ValueError("x")` and an async method prints `Try(lambda: self.fetch()).except_(ValueError, lambda e: e.message()).await_()`
- **THEN** it prints `x`

#### Scenario: A timeout is caught
- **WHEN** an async method prints `Try(lambda: AsyncWith(lambda: Async.timeout(0.01)).do(lambda t: Async.sleep(1))).except_(TimeoutError, lambda e: "late").await_()`
- **THEN** it prints `late`

#### Scenario: A handler that awaits
- **WHEN** a handler is `lambda e: self.fallback()` and `fallback` is an async method answering `"cached"`
- **THEN** the awaited `Try` answers `cached`

#### Scenario: else_ receives the awaited value
- **WHEN** `fetch` answers `2` and an async method prints `Try(lambda: self.fetch()).else_(lambda n: n * 10).await_()`
- **THEN** it prints `20`

### Requirement: An awaited Try needs a coroutine and runs once
An awaited `Try` SHALL refuse a block that answers no coroutine, naming
`run()`, and SHALL refuse to run a second time as `run()` does.

#### Scenario: A block that does not await
- **WHEN** an async method runs `Try(lambda: 1).await_()`
- **THEN** a `TypeError` is raised reading `the Try block must answer a coroutine, got an int — use #run for a block that does not await`

#### Scenario: Awaited after run
- **WHEN** a `Try` was already run and an async method sends it `.await_()`
- **THEN** a `RuntimeError` is raised reading `Try has already been executed; create a new Try instance to retry.`

### Requirement: run and finally_ refuse a block that answers a coroutine
`run()` and `finally_()` SHALL refuse a protected block that answers a
coroutine, since its failure would be raised only when it is awaited,
outside the guard. The coroutine SHALL be closed, so no "never awaited"
warning follows the refusal.

#### Scenario: run
- **WHEN** a program runs `Try(lambda: obj.fetch()).run()`
- **THEN** a `TypeError` is raised reading `the Try block answered a coroutine, which raises only when awaited — send #await_ to the Try instead of #run`

#### Scenario: finally_
- **WHEN** a program runs `Try(lambda: obj.fetch()).finally_(lambda: 1)`
- **THEN** a `TypeError` is raised reading `the Try block answered a coroutine, which raises only when awaited — an awaited Try has no cleanup clause; use AsyncWith for one`

### Requirement: run and finally_ name a Try that has not run
When the protected block of `run()` or `finally_()` answers a `Try` that has
not run, the refusal SHALL name it as a `Try` that has not run, not as a
coroutine.

#### Scenario: run
- **WHEN** a program runs `Try(lambda: Try(lambda: 1)).run()`
- **THEN** a `TypeError` is raised reading `the Try block answered a Try that has not run — send #run to it`

#### Scenario: finally_
- **WHEN** a program runs `Try(lambda: Try(lambda: 1)).finally_(lambda: 1)`
- **THEN** a `TypeError` is raised reading `the Try block answered a Try that has not run — send #run to it`
