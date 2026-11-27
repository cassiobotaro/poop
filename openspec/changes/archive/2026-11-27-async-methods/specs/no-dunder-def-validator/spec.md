# Spec Delta

## ADDED Requirements

### Requirement: Only three dunders may be async
The validator SHALL refuse an `async def` in a class body whose name is a
dunder other than `__call__`, `__aenter__` and `__aexit__`, since Python
calls the others without awaiting them.

#### Scenario: An async __str__
- **WHEN** a class body contains `async def __str__(self): return "x"`
- **THEN** validation fails with `async def __str__ is forbidden — Python calls __str__ without awaiting it; only __call__, __aenter__ and __aexit__ may be async`

#### Scenario: An async __init__
- **WHEN** a class body contains `async def __init__(self): pass`
- **THEN** validation fails with `async def __init__ is forbidden — Python calls __init__ without awaiting it; only __call__, __aenter__ and __aexit__ may be async`

#### Scenario: The three that may be async
- **WHEN** a class body defines `async def __call__`, `async def __aenter__` and `async def __aexit__`
- **THEN** this validator reports nothing
