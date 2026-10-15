# range-transformer Specification

## Purpose
How `range(...)` written in a program is built: the arguments it takes and
the words it refuses a wrong one with.

## Requirements

### Requirement: range refuses a non-int argument in POOP's words
`range(...)` SHALL refuse a `start`, `stop` or `step` that is not an integer
with the sentence the other integer arguments in the language use, naming
the role, never `'str' object cannot be interpreted as an integer`.

#### Scenario: A str stop
- **WHEN** a program runs `range("a")`
- **THEN** a `TypeError` is raised reading `#range's stop must be an int, got a str`

#### Scenario: A float step
- **WHEN** a program runs `range(1, 5, 1.5)`
- **THEN** a `TypeError` is raised reading `#range's step must be an int, got a float`

#### Scenario: A Boolean is the integer it stands for
- **WHEN** a program prints `range(True, 3)`
- **THEN** it prints `range(1, 3)`
