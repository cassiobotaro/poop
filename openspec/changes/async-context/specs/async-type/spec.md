# Spec Delta

## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Async.timeout answers a Timeout
`Async.timeout(delay)` SHALL answer a `Timeout` for `delay` seconds, where
`delay` is an `int`, a `float` or `None`. Its behaviour is the
`timeout-type` capability's.

#### Scenario: Its class
- **WHEN** a program prints `Async.timeout(1).class_().name()`
- **THEN** it prints `Timeout`
