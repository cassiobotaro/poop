# no-poop-prefix-validator Specification

## Purpose

Where a `_poop_`-prefixed name is refused, so the runtime's reserved
bindings cannot be reached from a program by any spelling.

## Requirements

### Requirement: A parameter annotation is checked like any other position
The validator SHALL refuse a `_poop_` name in a parameter's annotation, as it
refuses one in a body, a return annotation or a parameter name.

#### Scenario: A reserved name as a parameter annotation
- **WHEN** `poop --validators-only` runs a file holding `class A(object):` with `def m(self, x: _poop_int): return x`
- **THEN** the report reads `poop: _poop_int is forbidden — names starting with _poop_ are reserved for the runtime` with the caret under the annotation, and the command exits 1

#### Scenario: A reserved name as a lambda parameter is still refused
- **WHEN** `poop --validators-only` runs a file holding `f = lambda _poop_x: 1`
- **THEN** the report reads `poop: _poop_x is forbidden — names starting with _poop_ are reserved for the runtime`
