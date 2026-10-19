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

### Requirement: Every object answers the paired null test
`if_none_if_not_none(none_block, present_block)` on a non-`none` object
SHALL run `present_block` with the receiver and answer its value, never
running `none_block`; `if_not_none_if_none(present_block, none_block)` SHALL
do the same with the arguments swapped. A class SHALL answer both as an
object does.

#### Scenario: A present value runs the second block
- **WHEN** a program prints `(5).if_none_if_not_none(lambda: "absent", lambda x: x + 1)`
- **THEN** it prints `6`

#### Scenario: A present block that answers none is the answer
- **WHEN** a program prints `(5).if_none_if_not_none(lambda: "absent", lambda x: None)`
- **THEN** it prints `None`

#### Scenario: The swapped twin
- **WHEN** a program prints `(5).if_not_none_if_none(lambda x: x + 1, lambda: "absent")`
- **THEN** it prints `6`

#### Scenario: Both arguments are checked on the receiver that runs neither
- **WHEN** a program sends `if_none_if_not_none(5, lambda x: x)` to `(5)`
- **THEN** a `TypeError` is raised reading `#if_none_if_not_none expects a block, got an int — write .if_none_if_not_none(lambda: …, lambda value: …)`

#### Scenario: A class is an object
- **WHEN** a program prints `int.if_none_if_not_none(lambda: "absent", lambda k: k.name())`
- **THEN** it prints `int`

### Requirement: The null tests hint the receiver's value as value
A refusal from `if_not_none` or either null pair, on `None` and on every
object, SHALL name the block's argument `value` in its hint, as `else_`
names the value it hands on, since the argument is the receiver's own value
and not an element of a collection.

#### Scenario: if_not_none on an object
- **WHEN** a program runs `(5).if_not_none(5)`
- **THEN** a `TypeError` is raised reading `#if_not_none expects a block, got an int — write .if_not_none(lambda value: …)`

#### Scenario: if_not_none on None
- **WHEN** a program runs `None.if_not_none(5)`
- **THEN** a `TypeError` is raised reading `#if_not_none expects a block, got an int — write .if_not_none(lambda value: …)`

#### Scenario: The swapped pair
- **WHEN** a program runs `(5).if_not_none_if_none(5, lambda: 1)`
- **THEN** a `TypeError` is raised reading `#if_not_none_if_none expects a block, got an int — write .if_not_none_if_none(lambda value: …, lambda: …)`
