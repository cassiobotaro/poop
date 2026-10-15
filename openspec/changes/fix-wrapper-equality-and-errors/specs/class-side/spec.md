# Spec Delta

## Purpose

The messages every class answers as an object — `print`, `format`,
`del_attr` and the rest — worded as the instance side words them.

## ADDED Requirements

### Requirement: Class-side del_attr words both refusals
`Klass.del_attr(name)` SHALL refuse an absent name with `<Klass> has no
attribute '<name>' to remove`, and a name every class answers with the
sentence assignment to it already uses.

#### Scenario: An absent name
- **WHEN** a program runs `A.del_attr("nope")` on `class A: pass`
- **THEN** an `AttributeError` is raised reading `A has no attribute 'nope' to remove`

#### Scenario: A class-side message
- **WHEN** a program runs `A.del_attr("name")`
- **THEN** an `AttributeError` is raised reading `#name is answered by every class — it cannot be rebound`

### Requirement: Class-side format checks its spec in POOP's words
`Klass.format(spec)` SHALL refuse a non-`Str` spec and an unknown format
code with the sentences the instance side answers.

#### Scenario: A non-str spec
- **WHEN** a program runs `A.format(5)`
- **THEN** a `TypeError` is raised reading `#format expects a str, got an int`

#### Scenario: An unknown code
- **WHEN** a program runs `A.format("d")`
- **THEN** a `ValueError` is raised whose message is the one `"x".format("d")` answers for the same code

### Requirement: Class-side print checks end in POOP's words
`Klass.print(end=…)` SHALL refuse a non-`Str` `end` as the instance side
does.

#### Scenario: A non-str end
- **WHEN** a program runs `A.print(end=5)`
- **THEN** a `TypeError` is raised reading `#print's end must be a str, got an int`
