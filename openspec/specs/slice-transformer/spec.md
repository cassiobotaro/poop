# slice-transformer Specification

## Purpose

How a `slice(...)` call is rewritten into POOP's `Slice`, keeping CPython's
rule that a lone argument is the stop.

## Requirements

### Requirement: A lone argument is the stop, counted at runtime
`slice(x)` SHALL build `slice(None, x, None)`, and the count of arguments
SHALL be taken from the values the call receives, not from the number of
expressions written, so a starred argument expands before the rule applies.

#### Scenario: A literal single argument
- **WHEN** a program runs `slice(5).print()`
- **THEN** the output is `slice(None, 5, None)`

#### Scenario: A starred argument carrying two values
- **WHEN** a program runs `xs = (1, 5)` and then `slice(*xs).print()`
- **THEN** the output is `slice(1, 5, None)`, as CPython answers for `slice(*(1, 5))`

#### Scenario: A starred argument carrying one value
- **WHEN** a program runs `xs = (5,)` and then `slice(*xs).print()`
- **THEN** the output is `slice(None, 5, None)`

#### Scenario: Too many arguments keep their refusal
- **WHEN** a program runs `slice(1, 2, 3, 4)`
- **THEN** a `TypeError` is raised whose message reads `slice is built from a stop, or a start and a stop and an optional step, got 4 arguments — write slice(stop) or slice(start, stop, step)`

### Requirement: A bare slice names an alias whose call converts
A bare `slice` — bound to a name, passed as a value, or used as a base
class — SHALL build through the same converter as the literal call, so a
lone argument is the stop and a fourth argument is refused in POOP's words.

#### Scenario: A rebound name builds the same slice
- **WHEN** a program runs `s = slice` and prints `s(5)`
- **THEN** it prints `slice(None, 5, None)`

#### Scenario: A subclass builds the same slice
- **WHEN** a program defines `class S(slice): pass` and prints `S(5)`
- **THEN** it prints `slice(None, 5, None)` and `S(5).class_().name()` prints `S`

#### Scenario: A rebound name refuses four arguments as the literal does
- **WHEN** a program runs `s = slice` and `s(1, 2, 3, 4)`
- **THEN** a `TypeError` is raised reading `slice is built from a stop, or a start and a stop and an optional step, got 4 arguments — write slice(stop) or slice(start, stop, step)`
