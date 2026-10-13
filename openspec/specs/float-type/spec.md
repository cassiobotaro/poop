# float-type Specification

## Purpose

The messages a `Float` value and the `float` class answer in POOP, mirroring
CPython's `float` message for message and wording every refusal as a message
sent to an object.

## Requirements

### Requirement: The float class converts a real number with from_number
The `float` class SHALL answer `from_number(x)` with a `Float` holding the
value of `x`, for any `x` that is an integer, a boolean or a float, as Python
3.14's `float.from_number` does. A subclass of `float` SHALL answer an instance
of itself.

#### Scenario: An integer becomes a float
- **WHEN** a program sends `float.from_number(3)`
- **THEN** the answer prints `3.0` and is a `float`

#### Scenario: A boolean is the integer it stands for
- **WHEN** a program sends `float.from_number(True)`
- **THEN** the answer prints `1.0`

#### Scenario: A float is answered unchanged
- **WHEN** a program sends `float.from_number(2.5)`
- **THEN** the answer equals `2.5`

#### Scenario: A subclass answers itself
- **WHEN** a program defines `class Money(float)` and sends `Money.from_number(3)`
- **THEN** the answer is an instance of `Money`

### Requirement: from_number refuses a non-number in POOP's wording
`float.from_number` SHALL refuse a string, a complex, a collection or any other
non-real argument with a `TypeError` whose message names the message and the
argument's class in POOP's vocabulary, and never CPython's
`must be real number, not str`.

#### Scenario: A string is refused
- **WHEN** a program sends `float.from_number("3")`
- **THEN** a `TypeError` is raised whose message reads `#from_number expects a real number, got a str`

#### Scenario: A complex is refused
- **WHEN** a program sends `float.from_number(1j)`
- **THEN** a `TypeError` is raised whose message reads `#from_number expects a real number, got a complex`

#### Scenario: The refusal is catchable by its mirror
- **WHEN** a program wraps `float.from_number("x")` in `Try(...).except_(TypeError, handler).run()`
- **THEN** the handler runs
