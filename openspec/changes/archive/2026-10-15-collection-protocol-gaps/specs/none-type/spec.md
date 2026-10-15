# Spec Delta

## Purpose

The messages `none` answers in POOP: the null-object protocol that replaces
`x is None` and the two-branch test that `if_none` and `if_not_none` cannot
express by chaining.

## ADDED Requirements

### Requirement: none runs the none branch of the paired test
`if_none_if_not_none(none_block, present_block)` on `none` SHALL run
`none_block` and answer its value, never running `present_block`;
`if_not_none_if_none` SHALL do the same with the arguments swapped.

#### Scenario: none runs the first block
- **WHEN** a program prints `None.if_none_if_not_none(lambda: "absent", lambda x: x + 1)`
- **THEN** it prints `absent`

#### Scenario: The swapped twin
- **WHEN** a program prints `None.if_not_none_if_none(lambda x: x + 1, lambda: "absent")`
- **THEN** it prints `absent`

#### Scenario: The branch not taken is still checked
- **WHEN** a program sends `if_none_if_not_none(lambda: 1, 5)` to `None`
- **THEN** a `TypeError` is raised reading `#if_none_if_not_none expects a block, got an int — write .if_none_if_not_none(lambda: …, lambda x: …)`
