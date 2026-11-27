## ADDED Requirements

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
