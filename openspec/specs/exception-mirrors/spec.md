# exception-mirrors Specification

## Purpose
An exception instance built by a program — `ValueError("x")`, or an instance
of a class derived from one — answers the same messages a caught error does
and refuses the `BaseException` natives the class side already refuses.

## Requirements

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
`raise_()` on an exception instance SHALL refuse any argument with CPython's
wrong-arity sentence, naming the exception's class as CPython would. The
sentence has no hint to give, so POOP does not reword it.

#### Scenario: One argument
- **WHEN** a program runs `ValueError("x").raise_(1)`
- **THEN** a `TypeError` is raised reading `ValueError.raise_() takes 1 positional argument but 2 were given`
