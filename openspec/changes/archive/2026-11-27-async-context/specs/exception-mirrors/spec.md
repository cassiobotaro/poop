# Spec Delta

## ADDED Requirements

### Requirement: TimeoutError is mirrored under OSError
`TimeoutError` and `OSError` SHALL be names a program can write, and
`TimeoutError` SHALL sit under `OSError` as in CPython's tree, so a handler
for either catches a timeout.

#### Scenario: Caught by its parent
- **WHEN** an awaited `Try` over a body that outlasts `Async.timeout(0.01)` has `except_(OSError, lambda e: e.kind().name())`
- **THEN** it answers `TimeoutError`

#### Scenario: Raised and reported
- **WHEN** a program runs `TimeoutError.raise_("slow")` at module level
- **THEN** the program fails with `TimeoutError: slow`

#### Scenario: OSError's parent
- **WHEN** a program prints `TimeoutError.is_subclass(Exception)`
- **THEN** it prints `True`

### Requirement: CancelledError is mirrored outside Exception
`CancelledError` SHALL be a name a program can write, outside `Exception` as
in CPython's tree, and SHALL name the cause of an expired timeout.

#### Scenario: The cause of a timeout
- **WHEN** a program awaits a body that outlasts `Async.timeout(0.01)` with no handler
- **THEN** the uncaught report reads `TimeoutError` and then `caused by CancelledError`

#### Scenario: Read from a handler
- **WHEN** an awaited `Try` catches that `TimeoutError` with `lambda e: e.cause().kind().name()`
- **THEN** it answers `CancelledError`

#### Scenario: Not an Exception
- **WHEN** a program prints `CancelledError.is_subclass(Exception)`
- **THEN** it prints `False`
