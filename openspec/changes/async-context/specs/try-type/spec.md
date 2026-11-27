# Spec Delta

## ADDED Requirements

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
- **THEN** a `TypeError` is raised reading `the Try block must answer a coroutine, got an int — use .run() for a block that does not await`

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
- **THEN** a `TypeError` is raised reading `the Try block answered a coroutine, which raises only when awaited — send .await_() to the Try instead of .run()`

#### Scenario: finally_
- **WHEN** a program runs `Try(lambda: obj.fetch()).finally_(lambda: 1)`
- **THEN** a `TypeError` is raised reading `the Try block answered a coroutine, which raises only when awaited — an awaited Try has no cleanup clause; use AsyncWith for one`
