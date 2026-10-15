# no-class-keyword-validator Specification

## Purpose
A `class` statement is built from its bases alone: no keyword reaches
CPython's metaclass or `__init_subclass__` machinery from a POOP program.

## Requirements

### Requirement: A class statement refuses every keyword
The validator SHALL refuse each keyword argument of a `class` statement,
naming the keyword, so that `metaclass=`, a custom `__init_subclass__`
argument and `**kwargs` never reach the class builder.

#### Scenario: An arbitrary keyword is refused
- **WHEN** a program contains `class X(foo=1):`
- **THEN** validation fails with `class keyword 'foo' is forbidden — a class is built from its bases alone` pointing at the keyword

#### Scenario: A metaclass keyword is refused
- **WHEN** a program contains `class X(Object, metaclass=Object):`
- **THEN** validation fails with `class keyword 'metaclass' is forbidden — a class is built from its bases alone`

#### Scenario: A keyword splat is refused
- **WHEN** a program contains `class X(**opts):`
- **THEN** validation fails with `class keyword '**opts' is forbidden — a class is built from its bases alone`

#### Scenario: Bases alone pass
- **WHEN** a program contains `class X(Object):` and `class Y(X, list):`
- **THEN** this validator reports nothing
