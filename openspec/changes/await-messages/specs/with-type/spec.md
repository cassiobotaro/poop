## ADDED Requirements

### Requirement: With names a body that answers a Try that has not run
When `With.do(body)`'s body answers a `Try` that has not run, the refusal
SHALL name it as a `Try` that has not run, not as a coroutine. The manager
SHALL still be exited.

#### Scenario: A body that forgets run
- **WHEN** a program runs `With(lambda: cm).do(lambda r: Try(lambda: 1))` with a manager that prints `exit`
- **THEN** it prints `exit` and a `TypeError` is raised reading `the With body answered a Try that has not run — send #run to it`
