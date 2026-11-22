# Spec Delta

## ADDED Requirements

### Requirement: Class-side raise_ keeps no keyword for itself
`Klass.raise_(...)` SHALL hand every keyword the program wrote to the
exception's own constructor, whatever the keyword is named, and a class that
is not an error SHALL refuse with its one sentence whatever it is handed.

#### Scenario: A field named cls arrives by keyword
- **WHEN** `class Tagged(Exception)` stores `self.cls = cls` in `__init__(self, cls)` and a handler for `Tagged.raise_(cls="x")` prints `e.cls`
- **THEN** it prints `x`

#### Scenario: A class that is not an error refuses the same keyword
- **WHEN** a program defines `class Plain(Object)` and runs `Plain.raise_(cls="x")`
- **THEN** an `AttributeError` is raised reading `Plain cannot be raised — only a class descending from Exception can`
