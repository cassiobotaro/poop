# Spec Delta

## ADDED Requirements

### Requirement: With refuses a body that answers a coroutine
`With.do(body)` SHALL refuse a body that answers a coroutine, since the
coroutine would run after the manager has exited. The manager SHALL still
be exited, and the coroutine SHALL be closed, so no "never awaited" warning
follows the refusal.

#### Scenario: An awaiting body
- **WHEN** a program runs `With(lambda: cm).do(lambda r: obj.fetch())` with a manager that prints `exit`
- **THEN** it prints `exit` and a `TypeError` is raised reading `the With body answered a coroutine, which would run after the manager exits — use AsyncWith with an asynchronous context manager`
