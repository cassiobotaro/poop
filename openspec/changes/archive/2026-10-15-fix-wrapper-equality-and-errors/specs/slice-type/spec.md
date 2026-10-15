# Spec Delta

## ADDED Requirements

### Requirement: indices refuses a non-int bound as slice does
`indices(length)` on a `Slice` whose bound is not an integer SHALL refuse
with the sentence slicing a sequence with it answers, never CPython's
`slice indices must be integers or None or have an __index__ method`.

#### Scenario: A float stop
- **WHEN** a program runs `slice(1.5).indices(3)`
- **THEN** a `TypeError` is raised reading `slice bounds must be int, got a float`
