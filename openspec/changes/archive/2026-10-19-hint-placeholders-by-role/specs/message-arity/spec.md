# Spec Delta

## MODIFIED Requirements

### Requirement: A missing block in the branch family is refused with the hint
The branch messages (`if_true`, `if_false`, `if_true_if_false`,
`if_false_if_true`, `and_` and `or_` on a boolean; `if_none`, `if_not_none`
and both pairs on `None` and on every object; `while_true` and `while_false`
on a block) SHALL refuse a missing block with the sentence they give a
non-block, showing every block the message takes.

#### Scenario: if_true with nothing
- **WHEN** a program runs `True.if_true()`
- **THEN** a `TypeError` is raised reading `#if_true expects a block, got nothing — write .if_true(lambda: …)`

#### Scenario: A boolean pair with one block
- **WHEN** a program runs `True.if_true_if_false(lambda: 1)`
- **THEN** a `TypeError` is raised reading `#if_true_if_false expects a block, got nothing — write .if_true_if_false(lambda: …, lambda: …)`

#### Scenario: A boolean pair handed a non-block
- **WHEN** a program runs `True.if_false_if_true(5, 5)`
- **THEN** a `TypeError` is raised reading `#if_false_if_true expects a block, got an int — write .if_false_if_true(lambda: …, lambda: …)`

#### Scenario: and_ with nothing
- **WHEN** a program runs `True.and_()`
- **THEN** a `TypeError` is raised reading `#and_ expects a block, got nothing — write .and_(lambda: …)`

#### Scenario: if_none on None
- **WHEN** a program runs `None.if_none()`
- **THEN** a `TypeError` is raised reading `#if_none expects a block, got nothing — write .if_none(lambda: …)`

#### Scenario: A null pair on an object
- **WHEN** a program runs `(5).if_none_if_not_none()`
- **THEN** a `TypeError` is raised reading `#if_none_if_not_none expects a block, got nothing — write .if_none_if_not_none(lambda: …, lambda value: …)`

#### Scenario: while_true with nothing
- **WHEN** a program runs `(lambda: True).while_true()`
- **THEN** a `TypeError` is raised reading `#while_true expects a block, got nothing — write .while_true(lambda: …)`
