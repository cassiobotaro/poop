# Spec Delta

## MODIFIED Requirements

### Requirement: Every object answers the paired null test
`if_none_if_not_none(none_block, present_block)` on a non-`none` object
SHALL run `present_block` with the receiver and answer its value, never
running `none_block`; `if_not_none_if_none(present_block, none_block)` SHALL
do the same with the arguments swapped. A class SHALL answer both as an
object does.

#### Scenario: A present value runs the second block
- **WHEN** a program prints `(5).if_none_if_not_none(lambda: "absent", lambda x: x + 1)`
- **THEN** it prints `6`

#### Scenario: A present block that answers none is the answer
- **WHEN** a program prints `(5).if_none_if_not_none(lambda: "absent", lambda x: None)`
- **THEN** it prints `None`

#### Scenario: The swapped twin
- **WHEN** a program prints `(5).if_not_none_if_none(lambda x: x + 1, lambda: "absent")`
- **THEN** it prints `6`

#### Scenario: Both arguments are checked on the receiver that runs neither
- **WHEN** a program sends `if_none_if_not_none(5, lambda x: x)` to `(5)`
- **THEN** a `TypeError` is raised reading `#if_none_if_not_none expects a block, got an int — write .if_none_if_not_none(lambda: …, lambda value: …)`

#### Scenario: A class is an object
- **WHEN** a program prints `int.if_none_if_not_none(lambda: "absent", lambda k: k.name())`
- **THEN** it prints `int`

## ADDED Requirements

### Requirement: The null tests hint the receiver's value as value
A refusal from `if_not_none` or either null pair, on `None` and on every
object, SHALL name the block's argument `value` in its hint, as `else_`
names the value it hands on, since the argument is the receiver's own value
and not an element of a collection.

#### Scenario: if_not_none on an object
- **WHEN** a program runs `(5).if_not_none(5)`
- **THEN** a `TypeError` is raised reading `#if_not_none expects a block, got an int — write .if_not_none(lambda value: …)`

#### Scenario: if_not_none on None
- **WHEN** a program runs `None.if_not_none(5)`
- **THEN** a `TypeError` is raised reading `#if_not_none expects a block, got an int — write .if_not_none(lambda value: …)`

#### Scenario: The swapped pair
- **WHEN** a program runs `(5).if_not_none_if_none(5, lambda: 1)`
- **THEN** a `TypeError` is raised reading `#if_not_none_if_none expects a block, got an int — write .if_not_none_if_none(lambda value: …, lambda: …)`

