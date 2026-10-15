# int-type Specification

## Purpose
The messages an `Int` answers in POOP, mirroring CPython's `int` message for
message and admitting a `Boolean` wherever CPython admits one.

## Requirements

### Requirement: pow admits a Boolean modulus
`pow(exponent, modulus)` SHALL accept a `Boolean` modulus as the integer it
stands for, as every index-taking message does.

#### Scenario: A True modulus
- **WHEN** a program prints `(2).pow(3, True)`
- **THEN** it prints `0`

#### Scenario: A False modulus is zero
- **WHEN** a program runs `(2).pow(3, False)`
- **THEN** a `ValueError` is raised with the sentence `(2).pow(3, 0)` answers
