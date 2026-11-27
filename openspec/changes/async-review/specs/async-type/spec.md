## ADDED Requirements

### Requirement: A refusal from Async leaves no coroutine unawaited
When `Async.run` or `Async.gather` refuses a send, it SHALL close every
coroutine it was handed, so the refusal is not followed by CPython's
`RuntimeWarning` that a coroutine was never awaited.

#### Scenario: Gather refuses a later argument
- **WHEN** a program runs `Async.gather(obj.a(), 5)`
- **THEN** a `TypeError` is raised reading `#gather expects coroutines, got an int`, and no `RuntimeWarning` naming `a` is emitted

#### Scenario: Run inside run
- **WHEN** an async method sends `Async.run(obj.other())`
- **THEN** a `RuntimeError` is raised reading `asyncio.run() cannot be called from a running event loop`, and no `RuntimeWarning` naming `other` is emitted
