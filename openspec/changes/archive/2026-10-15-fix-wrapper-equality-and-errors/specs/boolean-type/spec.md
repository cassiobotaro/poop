# Spec Delta

## Purpose

The messages the two `Boolean` singletons answer in POOP, mirroring CPython's
`bool` and the Smalltalk boolean protocol.

## ADDED Requirements

### Requirement: Both singletons answer the one bool class
`True.class_()` and `False.class_()` SHALL answer the same class, equal to
the bare name `bool`, whose `superclass()` is `object` — the two rungs of
the tower are separate classes in POOP, so `bool` sits beside `int`, not
under it.

#### Scenario: class_ equals bool
- **WHEN** a program prints `True.class_() == bool` and `True.class_() == False.class_()`
- **THEN** both print `True`

#### Scenario: The ladder has one bool rung
- **WHEN** a program prints `True.class_().superclass().name()`
- **THEN** it prints `object`

### Requirement: xor and eqv take a Boolean
`xor` and `eqv` SHALL refuse a non-`Boolean` argument with the family's
sentence and SHALL always answer a `Boolean`.

#### Scenario: An int is refused
- **WHEN** a program sends `xor(5)` to `False`
- **THEN** a `TypeError` is raised reading `#xor expects a bool, got an int`

#### Scenario: A str is refused by eqv
- **WHEN** a program sends `eqv("abc")` to `True`
- **THEN** a `TypeError` is raised reading `#eqv expects a bool, got a str`

#### Scenario: Two booleans
- **WHEN** a program prints `True.xor(False)` and `True.eqv(True)`
- **THEN** both print `True`
