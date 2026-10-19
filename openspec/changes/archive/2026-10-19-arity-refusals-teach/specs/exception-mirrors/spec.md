# Spec Delta

## MODIFIED Requirements

### Requirement: raise_ on a built exception takes no argument
`raise_()` on an exception instance SHALL refuse any argument with CPython's
wrong-arity sentence, naming the exception's class as CPython would. The
sentence has no hint to give, so POOP does not reword it.

#### Scenario: One argument
- **WHEN** a program runs `ValueError("x").raise_(1)`
- **THEN** a `TypeError` is raised reading `ValueError.raise_() takes 1 positional argument but 2 were given`
