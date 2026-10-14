# str-transformer Specification

## Purpose

Which string constants are wrapped into `Str` at parse time, and which one
is left alone.

## Requirements

### Requirement: A docstring is left as a docstring
The first statement of a class or function body, when it is a bare string
literal, SHALL be left as a raw constant so CPython stores it as the
docstring and nothing is built on each call. Every other string literal is
still wrapped, a module's first statement included: at the REPL that is an
expression whose value is shown and asked about.

#### Scenario: A method docstring in the transformed dump
- **WHEN** `poop --transformers-only` runs a file holding `class A(object):` with `def m(self):`, the docstring `"""A method."""` and `return "x"`
- **THEN** the dump shows `"""A method."""` as the method's first statement, unwrapped, and `return _poop_str('x')` after it

#### Scenario: A class docstring in the transformed dump
- **WHEN** `poop --transformers-only` runs a file holding `class A(object):` with the docstring `"""A class."""` and a method
- **THEN** the dump shows `"""A class."""` as the class's first statement, unwrapped

#### Scenario: A module's first string is a value
- **WHEN** the REPL is given the input `"abc"` and then `:methods "abc"`
- **THEN** the first input echoes `'abc'` as a `Str` does and the second lists what a `str` understands, `class_name` among them

#### Scenario: A string that is not first is still wrapped
- **WHEN** `poop --transformers-only` runs a file holding a method whose body is `x = 1` followed by `"not a docstring"`
- **THEN** the dump shows `_poop_str('not a docstring')` for the second statement
