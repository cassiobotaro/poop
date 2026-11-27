## ADDED Requirements

### Requirement: Async.run and Async.gather accept an awaited Try
`Async.run` and `Async.gather` SHALL accept a `Try` wherever they accept a
coroutine, and SHALL run it as an awaited `Try` runs, its block's coroutine
awaited inside the guard.

#### Scenario: Running a Try
- **WHEN** an async method `fails` raises `ValueError("x")` and a program prints `Async.run(Try(lambda: obj.fails()).except_(ValueError, lambda e: "caught"))`
- **THEN** it prints `caught`

#### Scenario: Gathering a Try
- **WHEN** an async method runs `Async.gather(self.answer(), Try(lambda: self.fails()).except_(ValueError, lambda e: 0)).await_().repr().print()` with `answer` answering `42`
- **THEN** it prints `[42, 0]`
