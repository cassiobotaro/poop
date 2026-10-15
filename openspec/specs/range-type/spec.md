# range-type Specification

## Purpose
The messages a `Range` answers in POOP, mirroring CPython's `range` and the
collection protocol every other sequence in the language follows.

## Requirements

### Requirement: An empty range is falsy
A `Range` SHALL be falsy when it holds no element and truthy otherwise, so
`not_` and `assert_` read it as every other collection.

#### Scenario: not_ on an empty range
- **WHEN** a program prints `range(0).not_()` and `range(5, 2).not_()`
- **THEN** both print `True`

#### Scenario: assert_ on an empty range
- **WHEN** a program runs `range(0).assert_("empty")`
- **THEN** an `AssertionError` is raised reading `empty`

#### Scenario: A non-empty range is truthy
- **WHEN** a program prints `range(3).not_()`
- **THEN** it prints `False`

### Requirement: includes answers membership
`includes(x)` on a `Range` SHALL answer whether `x` is one of its elements,
admitting a `Boolean` as the integer it stands for.

#### Scenario: A held element
- **WHEN** a program prints `range(0, 10, 2).includes(4)` and `range(2).includes(True)`
- **THEN** both print `True`

#### Scenario: An absent element
- **WHEN** a program prints `range(0).includes(0)` and `range(0, 10, 2).includes(5)`
- **THEN** both print `False`
