# block-arity Specification

## Purpose

How a block refuses a call that hands it the wrong arguments: the sentence is
always POOP's, names the block and the counts, and never a Python name, a
Python calling convention or an internal of the interpreter.

## Requirements

### Requirement: A block made from a builtin's method refuses wrong arity in POOP's wording
A block answered by `get_attr` for a method or classmethod of a builtin
wrapper SHALL refuse a call with the wrong number of arguments with POOP's
arity sentence, exactly as a block literal does, regardless of how the
method's parameters are annotated in the interpreter's own source.

#### Scenario: A classmethod fetched by name and called with nothing
- **WHEN** a program runs `f = int.get_attr("from_bytes")` and then `f()`
- **THEN** a `TypeError` is raised whose message reads `block expects 1 to 2 arguments, got 0`

#### Scenario: A classmethod with an optional parameter
- **WHEN** a program runs `f = dict.get_attr("fromkeys")` and then `f()`
- **THEN** a `TypeError` is raised whose message reads `block expects 1 to 2 arguments, got 0`

#### Scenario: No interpreter name reaches the program
- **WHEN** a program calls any block made by `get_attr` from a builtin wrapper's method with the wrong number of arguments
- **THEN** the error is a `TypeError`, not a `NameError`, and its message contains none of the interpreter's own class names (`Bytes`, `Iterable`, `NoneClass`, `Callable`)

### Requirement: A block made from a builtin's method refuses an unknown keyword in POOP's wording
Such a block SHALL refuse a keyword argument it does not take with POOP's
keyword sentence, naming the keyword the program wrote.

#### Scenario: An unexpected keyword
- **WHEN** a program runs `f = int.get_attr("from_bytes")` and then `f(b"\x01", nope=1)`
- **THEN** a `TypeError` is raised whose message names `nope` and begins with `block`
