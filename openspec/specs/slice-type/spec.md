# slice-type Specification

## Purpose

The `Slice` wrapper and the `slice` message every sequence answers with it.

## Requirements

### Requirement: A sequence's slice takes a Slice or bounds, not both
A sequence's `slice` message SHALL accept either one `Slice` or up to three
bounds (start, stop, step). A `Slice` followed by any bound SHALL be refused
rather than have the bound dropped.

#### Scenario: A Slice alone
- **WHEN** a program runs `[0, 1, 2, 3, 4].slice(slice(1, 3)).print()`
- **THEN** the output is `1 2`

#### Scenario: Bounds alone
- **WHEN** a program runs `[0, 1, 2, 3, 4].slice(1, 3).print()`
- **THEN** the output is `1 2`

#### Scenario: A Slice and a stop
- **WHEN** a program runs `[0, 1, 2, 3, 4].slice(slice(1, 3), 4)`
- **THEN** a `TypeError` is raised whose message reads `#slice takes a slice or bounds, not both — write .slice(slice(1, 3)) or .slice(1, 3)`

#### Scenario: A Slice and a step keyword
- **WHEN** a program runs `"abcde".slice(slice(1, 3), step=2)`
- **THEN** a `TypeError` is raised whose message reads `#slice takes a slice or bounds, not both — write .slice(slice(1, 3)) or .slice(1, 3)`

### Requirement: indices refuses a non-int bound as slice does
`indices(length)` on a `Slice` whose bound is not an integer SHALL refuse
with the sentence slicing a sequence with it answers, never CPython's
`slice indices must be integers or None or have an __index__ method`.

#### Scenario: A float stop
- **WHEN** a program runs `slice(1.5).indices(3)`
- **THEN** a `TypeError` is raised reading `slice bounds must be int, got a float`
