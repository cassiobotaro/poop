# async-type Specification

## Purpose
`Async`, the injected class that runs coroutines: its class-side messages
`run`, `sleep` and `gather`, what each answers, and what each refuses.

## Requirements

### Requirement: Async is reachable and has no instances
`Async` SHALL be in scope in every program with no import, and SHALL refuse
to be instantiated.

#### Scenario: Its name
- **WHEN** a program runs `Async.name().print()`
- **THEN** it prints `Async`

#### Scenario: Instantiating it
- **WHEN** a program runs `Async()`
- **THEN** a `TypeError` is raised reading `Async has no instances — send run, sleep, gather or timeout to the class`

#### Scenario: Shadowing it
- **WHEN** a program contains `Async = 1`
- **THEN** validation fails as it does for `Try = 1`

### Requirement: Async.run drives a coroutine to its answer
`Async.run(coroutine)` SHALL run the coroutine on a new event loop and
answer its value. It SHALL refuse a value that cannot be awaited, and SHALL
fail as CPython does when sent from inside a running coroutine.

#### Scenario: Running a method
- **WHEN** an async method `main` answers `42` and a program runs `Async.run(obj.main()).print()`
- **THEN** it prints `42`

#### Scenario: A value that cannot be awaited
- **WHEN** a program runs `Async.run(5)`
- **THEN** a `TypeError` is raised reading `#run expects a coroutine, got an int`

#### Scenario: Run inside run
- **WHEN** an async method sends `Async.run(obj.other())`
- **THEN** a `RuntimeError` is raised reading `asyncio.run() cannot be called from a running event loop`

### Requirement: Async.sleep suspends and answers its result
`Async.sleep(delay, result=none)` SHALL answer a coroutine that, awaited,
suspends for `delay` seconds and answers `result`. `delay` SHALL be an `int`
or a `float`.

#### Scenario: Answers none by default
- **WHEN** an async method prints `Async.sleep(0).await_().is_none()`
- **THEN** it prints `True`

#### Scenario: Answers the given result
- **WHEN** an async method prints `Async.sleep(0, "done").await_()`
- **THEN** it prints `done`

#### Scenario: A delay of the wrong kind
- **WHEN** a program runs `Async.sleep("1")`
- **THEN** a `TypeError` is raised reading `#sleep expects a number, got a str`

### Requirement: Async.gather awaits coroutines together
`Async.gather(*coroutines)` SHALL answer a coroutine that, awaited, runs the
given coroutines concurrently and answers a `List` of their values in the
order given. The first failure SHALL propagate, as CPython's does.

#### Scenario: Values in order
- **WHEN** `a` answers `1` after `Async.sleep(0.02)`, `b` answers `2` after `Async.sleep(0.01)`, and an async method runs `Async.gather(obj.a(), obj.b()).await_().repr().print()`
- **THEN** it prints `[1, 2]`

#### Scenario: Concurrently
- **WHEN** three coroutines each await `Async.sleep(0.1)` and are gathered
- **THEN** the gather completes in well under 0.3 seconds

#### Scenario: A mapped collection is gathered
- **WHEN** an async method runs `Async.gather(*[1, 2].map(lambda n: obj.double(n))).await_().repr().print()` with `double` answering `n * 2`
- **THEN** it prints `[2, 4]`

#### Scenario: A value that cannot be awaited
- **WHEN** a program runs `Async.gather(obj.a(), 5)`
- **THEN** a `TypeError` is raised reading `#gather expects coroutines, got an int`

### Requirement: Async.timeout answers a Timeout
`Async.timeout(delay)` SHALL answer a `Timeout` for `delay` seconds, where
`delay` is an `int`, a `float` or `None`. Its behaviour is the
`timeout-type` capability's.

#### Scenario: Its class
- **WHEN** a program prints `Async.timeout(1).class_().name()`
- **THEN** it prints `Timeout`

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
