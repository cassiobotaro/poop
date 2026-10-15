# Spec Delta

## Purpose

`Try`, the construct replacing `try`/`except`/`finally`: how it is built,
chained and run.

## ADDED Requirements

### Requirement: Try counts its arguments in POOP's words
`Try(...)` SHALL refuse no argument or more than one with a sentence naming
the construct and the block it takes, never `__init__` or `positional
argument`.

#### Scenario: No argument
- **WHEN** a program runs `Try()`
- **THEN** a `TypeError` is raised reading `Try takes one block, got nothing — write Try(lambda: …)`

#### Scenario: Two arguments
- **WHEN** a program runs `Try(lambda: 1, lambda: 2)`
- **THEN** a `TypeError` is raised reading `Try takes one block, got 2 arguments — write Try(lambda: …)`
