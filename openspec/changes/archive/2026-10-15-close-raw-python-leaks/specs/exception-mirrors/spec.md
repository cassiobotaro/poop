# Spec Delta

## Purpose

An exception instance built by a program — `ValueError("x")`, or an instance
of a class derived from one — answers the same messages a caught error does
and refuses the `BaseException` natives the class side already refuses.

## ADDED Requirements

### Requirement: A built exception answers message, kind and raise_
An exception instance SHALL answer `message()` with its text as a `Str`,
`kind()` with its class, and `raise_()` by signalling itself, so it can be
handed around and raised later like a caught `Error`.

#### Scenario: message and kind
- **WHEN** a program runs `e = ValueError("x")`
- **THEN** `e.message()` prints `x` and `e.kind().name()` prints `ValueError`

#### Scenario: A built exception is raised later
- **WHEN** a program runs `Try(lambda: ValueError("x").raise_()).except_(ValueError, lambda e: e.message().print()).run()`
- **THEN** it prints `x`

#### Scenario: A user subclass with fields
- **WHEN** a program defines `class Field(Exception)` whose `__init__(self, code)` stores `self.code` and runs `Field(7).raise_()` inside a `Try`
- **THEN** the handler's `e.kind().name()` prints `Field`

### Requirement: A built exception prints as a caught one does
`print()` on an exception instance SHALL produce `<Kind>: <message>`, the bare
kind when the message is empty, and `repr()` SHALL answer the same text,
never CPython's `ValueError('x')`.

#### Scenario: print
- **WHEN** a program runs `ValueError("x").print()`
- **THEN** it prints `ValueError: x`

#### Scenario: An empty message
- **WHEN** a program runs `ValueError().print()`
- **THEN** it prints `ValueError`

### Requirement: The BaseException natives are refused on the instance
`args`, `add_note` and `with_traceback` SHALL be refused on an exception
instance with the sentences the class side answers.

#### Scenario: args
- **WHEN** a program reads `ValueError("x").args`
- **THEN** an `AttributeError` is raised reading `ValueError does not understand #args — #args is Python's; a caught error answers #message`

#### Scenario: add_note
- **WHEN** a program sends `add_note("n")` to `ValueError("x")`
- **THEN** an `AttributeError` is raised reading `ValueError does not understand #add_note — #add_note is Python's; POOP does not offer it`
