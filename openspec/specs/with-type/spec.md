# with-type Specification

## Purpose
`With`, the construct replacing the `with` statement: how it is built and
run.

## Requirements

### Requirement: With counts its arguments in POOP's words
`With(...)` SHALL refuse no argument or more than one with a sentence naming
the construct and the block it takes, never `__init__` or `positional
argument`.

#### Scenario: No argument
- **WHEN** a program runs `With()`
- **THEN** a `TypeError` is raised reading `With takes one block, got nothing — write With(lambda: …)`

#### Scenario: Two arguments
- **WHEN** a program runs `With(lambda: 1, lambda: 2)`
- **THEN** a `TypeError` is raised reading `With takes one block, got 2 arguments — write With(lambda: …)`
