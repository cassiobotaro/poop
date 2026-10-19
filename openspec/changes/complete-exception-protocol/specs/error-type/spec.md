# Spec Delta

## ADDED Requirements

### Requirement: A caught error answers its explicit cause
A caught error SHALL answer `cause()` with the error wrapping the exception
it was raised from, and `none` when it was raised from nothing or from
`None`.

#### Scenario: Raised from a cause
- **WHEN** a handler for `ZeroDivisionError` runs `KeyError("outer").raise_from(e)` and an outer handler for `KeyError` prints `e.cause().message()`
- **THEN** it prints `division by zero`

#### Scenario: No cause
- **WHEN** a handler for `ValueError` caught `ValueError.raise_("x")` and prints `e.cause().is_none()`
- **THEN** it prints `True`

### Requirement: A caught error answers the context it was raised in
A caught error SHALL answer `context()` with the error that was being
handled when it was raised, and `none` when none was or when the context
was suppressed by `raise_from`.

#### Scenario: Raised inside a handler
- **WHEN** a handler for `ZeroDivisionError` runs `KeyError.raise_("outer")` and an outer handler for `KeyError` prints `e.context().kind().name()`
- **THEN** it prints `ZeroDivisionError`

#### Scenario: Suppressed by raise_from
- **WHEN** a handler for `ZeroDivisionError` runs `KeyError("outer").raise_from(ValueError("inner"))` and an outer handler for `KeyError` prints `e.context().is_none()`
- **THEN** it prints `True`

#### Scenario: An error POOP composed carries no context
- **WHEN** a handler for `IndexError` catches `[1].at(5)` and prints `e.context().is_none()`
- **THEN** it prints `True`

### Requirement: raise_ on a caught error takes no argument
`raise_()` on a caught error SHALL refuse any argument with a sentence of
POOP's, never CPython's `positional argument` wording.

#### Scenario: One argument
- **WHEN** a handler for `ValueError` runs `e.raise_(1)`
- **THEN** a `TypeError` is raised reading `#raise_ takes no argument on a caught error, got 1 argument`
