# Spec Delta

## Purpose

What a handler can ask of the error it was handed: the exception's message
and kind, the state a program's own exception class stored, and identity
across re-raising.

## ADDED Requirements

### Requirement: A caught error forwards the exception's own state
A caught error SHALL answer a public attribute that the exception's class
stored on the instance, and `has_attr`, `get_attr` and `dir` SHALL see it;
names that are methods of the exception or dunders SHALL stay refused.

#### Scenario: A field stored by __init__ is read in the handler
- **WHEN** `class Field(Exception)` stores `self.code = code` in `__init__` and a handler for `Field.raise_(code=7)` prints `e.code`
- **THEN** it prints `7`

#### Scenario: has_attr and dir see the field
- **WHEN** the same handler prints `e.has_attr("code")` and `e.dir().includes("code")`
- **THEN** both print `True`

#### Scenario: A native method is still refused
- **WHEN** the same handler reads `e.add_note`
- **THEN** an `AttributeError` is raised reading `Field does not understand #add_note — #add_note is Python's; POOP does not offer it`

### Requirement: Errors wrapping one exception are one error
Two caught errors that stand for the same exception object SHALL compare
equal and hash alike, so the error re-signalled by `raise_` is the one first
caught.

#### Scenario: The re-raised error equals the first
- **WHEN** a program keeps the error `e1` from one `Try`, runs `e1.raise_()` inside another and compares the new handler's `e` with `e1`
- **THEN** `e == e1` prints `True` and `e.hash() == e1.hash()` prints `True`
