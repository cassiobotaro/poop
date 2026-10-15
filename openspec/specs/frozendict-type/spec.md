# frozendict-type Specification

## Purpose
The messages a `FrozenDict` answers in POOP, mirroring Python 3.15's
`frozendict`.

## Requirements

### Requirement: hash names the value that cannot be hashed
`hash()` on a `FrozenDict` holding an unhashable value SHALL refuse by naming
the frozendict and the value's kind, not by saying the value has no place
as a dict key.

#### Scenario: A list value
- **WHEN** a program runs `frozendict({"a": [1]}).hash()`
- **THEN** a `TypeError` is raised reading `frozendict cannot be hashed — it holds a list, which cannot be`
