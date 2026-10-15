# Spec Delta

## ADDED Requirements

### Requirement: super() is sent from a method, never from a lambda
The validator SHALL refuse a `super()` call whose nearest enclosing function
is a `lambda`, since a lambda owns no class cell and CPython answers
`RuntimeError: super(): no arguments` at run time.

#### Scenario: super() inside a block in a method is refused
- **WHEN** a method body contains `(lambda: super().greet())()`
- **THEN** validation fails with `super() inside a lambda is forbidden — send it from the method and hand the block its answer`

#### Scenario: super() directly in a method passes
- **WHEN** a method body contains `return super().greet()`
- **THEN** this validator reports nothing

### Requirement: __init__ answers nothing
The validator SHALL refuse a `return` carrying a value whose nearest enclosing
function is a method named `__init__`, since CPython answers `__init__()
should return None` at run time.

#### Scenario: A value returned from __init__ is refused
- **WHEN** an `__init__` body contains `return 5`
- **THEN** validation fails with `return with a value in __init__ is forbidden — __init__ builds the receiver and answers nothing`

#### Scenario: A bare return passes
- **WHEN** an `__init__` body contains a bare `return`
- **THEN** this validator reports nothing
