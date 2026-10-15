# Spec Delta

## ADDED Requirements

### Requirement: print checks end and sep in POOP's words
`print(end=…)` on any object, and `print(sep=…)` on a sequence, SHALL refuse
a value that is not a `Str` with the family's sentence, never CPython's
`end must be None or a string, not int`.

#### Scenario: A non-str end
- **WHEN** a program runs `(5).print(end=5)`
- **THEN** a `TypeError` is raised reading `#print's end must be a str, got an int`

#### Scenario: A non-str sep on a list
- **WHEN** a program runs `[1].print(sep=5)`
- **THEN** a `TypeError` is raised reading `#print's sep must be a str, got an int`

#### Scenario: A positional end
- **WHEN** a program runs `"x".print(5)`
- **THEN** a `TypeError` is raised reading `#print's end must be a str, got an int`
