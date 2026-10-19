# Spec Delta

## MODIFIED Requirements

### Requirement: print checks end and sep in POOP's words
`print(end=…)` on any object, and `print(sep=…)` on a sequence, SHALL refuse
a value that is not a `Str` with the family's sentence, never CPython's
`end must be None or a string, not int`. `end`, `sep` and `flush` SHALL be
keyword-only, as in CPython's `print`, so a positional argument is a
wrong-arity call.

#### Scenario: A non-str end
- **WHEN** a program runs `(5).print(end=5)`
- **THEN** a `TypeError` is raised reading `#print's end must be a str, got an int`

#### Scenario: A non-str sep on a list
- **WHEN** a program runs `[1].print(sep=5)`
- **THEN** a `TypeError` is raised reading `#print's sep must be a str, got an int`

#### Scenario: A positional end
- **WHEN** a program runs `"x".print(5)`
- **THEN** a `TypeError` is raised reading `object.print() takes 1 positional argument but 2 were given`

#### Scenario: A positional argument with end
- **WHEN** a program runs `(5).print("x", end="")`
- **THEN** a `TypeError` is raised reading `object.print() takes 1 positional argument but 2 positional arguments (and 1 keyword-only argument) were given`

#### Scenario: A positional argument on a list
- **WHEN** a program runs `[1].print(5)`
- **THEN** a `TypeError` is raised reading `list.print() takes 1 positional argument but 2 were given`

#### Scenario: A positional argument on a class
- **WHEN** a program runs `int.print(5)`
- **THEN** a `TypeError` is raised reading `int.print() takes 1 positional argument but 2 were given`
