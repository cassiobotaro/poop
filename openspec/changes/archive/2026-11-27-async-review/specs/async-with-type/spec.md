## ADDED Requirements

### Requirement: A manager slot that cannot be awaited is refused in POOP's words
When a manager's asynchronous enter or exit answers a value that cannot be
awaited, awaiting `AsyncWith` SHALL fail with a `TypeError` that names the
manager's class, the slot as `enter` or `exit`, and what it answered, and
that names no dunder.

#### Scenario: A synchronous enter
- **WHEN** a class `Res` defines `def __aenter__(self): return self` with an async `__aexit__`, and an async method awaits `AsyncWith(lambda: Res()).do(lambda r: obj.g())`
- **THEN** a `TypeError` is raised reading `Res's asynchronous enter answered a Res, which cannot be awaited — write it as async def`, and the body does not run

#### Scenario: A synchronous exit
- **WHEN** a class `Res` defines an async `__aenter__` and `def __aexit__(self, kind, error, tb): return False`, and an async method awaits `AsyncWith(lambda: Res()).do(lambda r: obj.g())`
- **THEN** a `TypeError` is raised reading `Res's asynchronous exit answered a bool, which cannot be awaited — write it as async def`
