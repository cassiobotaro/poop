# Spec Delta

## Purpose

A leading underscore is an object's own state; the validator refuses
reaching for it by attribute and names a substitute the runtime honours.

## ADDED Requirements

### Requirement: The refusal names a real substitute
The validator's sentence SHALL not point at `get_attr`, which the runtime
refuses for a private name; it SHALL say the state is reached only by
`self` or `cls`, and otherwise by a message the object answers.

#### Scenario: Reading another object's private attribute
- **WHEN** a method body reads `other._x`
- **THEN** validation fails with `._x is forbidden — a leading underscore is an object's own state; only self and cls reach it, so send other a message that answers it`
