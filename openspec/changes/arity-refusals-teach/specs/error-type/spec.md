# Spec Delta

## MODIFIED Requirements

### Requirement: raise_ on a caught error takes no argument
`raise_()` on a caught error SHALL refuse any argument with CPython's
wrong-arity sentence, naming the class of the exception the error wraps.
The sentence has no hint to give, so POOP does not reword it.

#### Scenario: One argument
- **WHEN** a handler for `ValueError` runs `e.raise_(1)`
- **THEN** a `TypeError` is raised reading `ValueError.raise_() takes 1 positional argument but 2 were given`
