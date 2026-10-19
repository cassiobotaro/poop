# try-type Specification

## Purpose
`Try`, the construct replacing `try`/`except`/`finally`: how it is built,
chained and run.

## Requirements

### Requirement: Try counts its arguments in POOP's words
`Try(...)` SHALL refuse no argument or more than one with a sentence naming
the construct and the block it takes, never `__init__` or `positional
argument`.

#### Scenario: No argument
- **WHEN** a program runs `Try()`
- **THEN** a `TypeError` is raised reading `Try takes one block, got nothing — write Try(lambda: …)`

#### Scenario: Two arguments
- **WHEN** a program runs `Try(lambda: 1, lambda: 2)`
- **THEN** a `TypeError` is raised reading `Try takes one block, got 2 arguments — write Try(lambda: …)`

### Requirement: else_ runs on success and answers in its place
`Try` SHALL answer `else_(block)`, chainable like `except_`. When the
protected block raises nothing, the block SHALL be called with the
protected block's value, and its own value SHALL be what `run()` or
`finally_()` answers. When the protected block raises, the block SHALL not
run.

#### Scenario: The protected block succeeds
- **WHEN** a program prints `Try(lambda: int("21")).except_(ValueError, lambda e: -1).else_(lambda n: n * 2).run()`
- **THEN** it prints `42`

#### Scenario: The protected block raises
- **WHEN** a program prints `Try(lambda: int("x")).except_(ValueError, lambda e: -1).else_(lambda n: n * 2).run()`
- **THEN** it prints `-1`

#### Scenario: Through finally_
- **WHEN** a program prints `Try(lambda: 1).else_(lambda n: n + 1).finally_(lambda: "done".print())`
- **THEN** it prints `done` and then `2`

### Requirement: else_ is outside the handlers and before the cleanup
An exception raised by the `else_` block SHALL not be caught by any handler
registered with `except_` on the same `Try`, and the cleanup given to
`finally_` SHALL run after the `else_` block, whether it raised or not.

#### Scenario: A handler does not catch the else block
- **WHEN** a program runs `Try(lambda: 1).except_(ValueError, lambda e: "caught".print()).else_(lambda n: ValueError.raise_("late")).run()`
- **THEN** `caught` is not printed and the program fails with `ValueError: late`

#### Scenario: The cleanup runs after a failing else block
- **WHEN** a program runs `Try(lambda: 1).else_(lambda n: ValueError.raise_("late")).finally_(lambda: "cleanup".print())`
- **THEN** it prints `cleanup` and then fails with `ValueError: late`

### Requirement: else_ refuses a non-block and a second else
`else_` SHALL refuse an argument that is not a block where it was written,
and SHALL refuse being sent twice to one `Try`. A block of the wrong arity
SHALL be reported when it is called, in the words every block uses.

#### Scenario: Not a block
- **WHEN** a program runs `Try(lambda: 1).else_(5)`
- **THEN** a `TypeError` is raised reading `the else clause must be a block, got an int — write .else_(lambda value: …)`

#### Scenario: A second else
- **WHEN** a program runs `Try(lambda: 1).else_(lambda n: n).else_(lambda n: n)`
- **THEN** a `TypeError` is raised reading `Try already has an else clause — send #else_ once`

#### Scenario: A block that takes nothing
- **WHEN** a program runs `Try(lambda: 1).else_(lambda: 2).run()`
- **THEN** a `TypeError` is raised reading `block expects 0 arguments, got 1`
