# complex-type Specification

## Purpose

The messages a `Complex` value and the `complex` class answer in POOP,
mirroring CPython's `complex` message for message and wording every refusal as
a message sent to an object.

## Requirements

### Requirement: The complex class converts a number with from_number
The `complex` class SHALL answer `from_number(x)` with a `Complex` holding the
value of `x`, for any `x` that is an integer, a boolean, a float or a complex,
as Python 3.14's `complex.from_number` does. A subclass of `complex` SHALL
answer an instance of itself.

#### Scenario: A float becomes a complex
- **WHEN** a program sends `complex.from_number(2.5)`
- **THEN** the answer prints `(2.5+0j)`

#### Scenario: A complex is answered unchanged
- **WHEN** a program sends `complex.from_number(1j)`
- **THEN** the answer equals `1j`

#### Scenario: A boolean is the integer it stands for
- **WHEN** a program sends `complex.from_number(True)`
- **THEN** the answer prints `(1+0j)`

### Requirement: from_number refuses a non-number in POOP's wording
`complex.from_number` SHALL refuse a string, a collection or any other
non-numeric argument with a `TypeError` whose message names the message and
the argument's class in POOP's vocabulary, and never CPython's
`must be real number, not str`.

#### Scenario: A string is refused
- **WHEN** a program sends `complex.from_number("1")`
- **THEN** a `TypeError` is raised whose message reads `#from_number expects a number, got a str`

#### Scenario: A list is refused
- **WHEN** a program sends `complex.from_number([1])`
- **THEN** a `TypeError` is raised whose message reads `#from_number expects a number, got a list`
