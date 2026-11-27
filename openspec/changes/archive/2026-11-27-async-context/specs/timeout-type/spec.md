# Spec Delta

## Purpose
The `Timeout` that `Async.timeout(delay)` answers: an asynchronous context
manager that fails its body with `TimeoutError` once the delay passes.

## ADDED Requirements

### Requirement: A Timeout fails a body that outlasts it
Entered with `AsyncWith`, a `Timeout` SHALL let a body that finishes in time
answer its value, and SHALL fail a body that outlasts the delay with
`TimeoutError`. A delay of `None` SHALL never expire.

#### Scenario: In time
- **WHEN** an async method prints the awaited `AsyncWith(lambda: Async.timeout(1)).do(lambda t: Async.sleep(0, "ok"))`
- **THEN** it prints `ok`

#### Scenario: Too late
- **WHEN** an async method awaits `AsyncWith(lambda: Async.timeout(0.01)).do(lambda t: Async.sleep(1))`
- **THEN** a `TimeoutError` is raised

#### Scenario: No deadline
- **WHEN** an async method prints the awaited `AsyncWith(lambda: Async.timeout(None)).do(lambda t: Async.sleep(0.01, "ok"))`
- **THEN** it prints `ok`

### Requirement: The body receives the Timeout, which answers expired
The body SHALL receive the `Timeout` itself, which SHALL answer `expired()`
with a `Boolean` and print as `<Timeout>`.

#### Scenario: Not expired inside the body
- **WHEN** the body is `lambda t: obj.report(t)` and `report` prints `t.expired()`
- **THEN** it prints `False`

### Requirement: A Timeout is checked where it is built and entered once
`Async.timeout` SHALL refuse a delay that is not a number or `None`, and a
`Timeout` SHALL refuse to be entered twice as CPython does.

#### Scenario: A delay of the wrong kind
- **WHEN** a program runs `Async.timeout("1")`
- **THEN** a `TypeError` is raised reading `#timeout expects a number or None, got a str`

#### Scenario: Entered twice
- **WHEN** an async method awaits two `AsyncWith`s over the same `Timeout`
- **THEN** a `RuntimeError` is raised reading `Timeout has already been entered`

#### Scenario: Entered synchronously
- **WHEN** a program runs `With(lambda: Async.timeout(1)).do(lambda t: t)`
- **THEN** a `TypeError` is raised reading `Timeout does not support the context manager protocol — it cannot be entered`
