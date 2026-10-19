# Spec Delta

## ADDED Requirements

### Requirement: A built exception is raised from a cause
An exception instance SHALL answer `raise_from(cause)` by signalling itself
with `cause` as its cause, as `raise X from Y` does. `cause` SHALL be a
caught error or a built exception instance; `None` SHALL signal it with no
cause and its context suppressed, as `raise X from None` does.

#### Scenario: From a caught error
- **WHEN** a handler for `ZeroDivisionError` runs `KeyError("outer").raise_from(e)` and an outer handler for `KeyError` prints `e.cause().kind().name()`
- **THEN** it prints `ZeroDivisionError`

#### Scenario: From a built exception
- **WHEN** a handler for `KeyError` catches `KeyError("outer").raise_from(ValueError("inner"))` and prints `e.cause().message()`
- **THEN** it prints `inner`

#### Scenario: From None
- **WHEN** a handler for `ZeroDivisionError` runs `KeyError("outer").raise_from(None)` and an outer handler for `KeyError` prints `e.cause().is_none()` and `e.context().is_none()`
- **THEN** both print `True`

### Requirement: raise_from refuses anything but one exception or None
`raise_from` SHALL refuse a missing cause, more than one cause, a value that
is not an exception and an exception class, naming what it takes.

#### Scenario: A value
- **WHEN** a program runs `KeyError("outer").raise_from(5)`
- **THEN** a `TypeError` is raised reading `#raise_from takes an exception or None, got an int`

#### Scenario: A class
- **WHEN** a program runs `KeyError("outer").raise_from(ValueError)`
- **THEN** a `TypeError` is raised reading `#raise_from takes an exception or None, got the class ValueError`

#### Scenario: Nothing
- **WHEN** a program runs `KeyError("outer").raise_from()`
- **THEN** a `TypeError` is raised reading `#raise_from takes an exception or None, got nothing`

#### Scenario: Two causes
- **WHEN** a program runs `KeyError("outer").raise_from(ValueError("a"), ValueError("b"))`
- **THEN** a `TypeError` is raised reading `#raise_from takes an exception or None, got 2 arguments`

### Requirement: raise_ on a built exception takes no argument
`raise_()` on an exception instance SHALL refuse any argument with a
sentence of POOP's, never CPython's `positional argument` wording.

#### Scenario: One argument
- **WHEN** a program runs `ValueError("x").raise_(1)`
- **THEN** a `TypeError` is raised reading `#raise_ takes no argument once the exception is built, got 1 argument`
