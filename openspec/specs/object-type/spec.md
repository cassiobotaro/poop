# object-type Specification

## Purpose

The protocol every POOP object answers, instance side and class side:
identity, reflection, printing and the substitutes for banned builtins.

## Requirements

### Requirement: get_attr takes at most one default
`get_attr(name)` and `get_attr(name, default)` SHALL be the two shapes of the
message, on an instance and on a class alike. A third positional argument
SHALL be refused as any message refuses too many arguments, and SHALL never
be answered in silence nor reported in CPython's `getattr` wording.

#### Scenario: A missing name with a default
- **WHEN** a program runs `(5).get_attr("nope", 7).print()`
- **THEN** the output is `7`

#### Scenario: Two defaults on an instance
- **WHEN** a program runs `(5).get_attr("nope", 1, 2)`
- **THEN** a `TypeError` is raised whose message reads `object.get_attr() takes from 2 to 3 positional arguments but 4 were given`, and the word `getattr` appears nowhere in it

#### Scenario: Two defaults on a class
- **WHEN** a program runs `int.get_attr("nope", 1, 2)`
- **THEN** a `TypeError` is raised whose message reads `get_attr() takes from 2 to 3 positional arguments but 4 were given`, and nothing is answered

### Requirement: does_not_understand receives the selector as a Str
When a message is not answered, the receiver's `does_not_understand` hook
SHALL be handed the selector as a POOP `Str`, so a hook that answers the name
answers an object every message reaches.

#### Scenario: The hook's answer is a POOP string
- **WHEN** a class defines `def does_not_understand(self, name): return name` and a program prints `P().foo`
- **THEN** it prints `foo` and `P().foo.upper()` answers `FOO`

#### Scenario: The hook can compare the selector
- **WHEN** the hook body is `return name.startswith("get_")`
- **THEN** `P().get_x` answers `True` as a POOP Boolean
