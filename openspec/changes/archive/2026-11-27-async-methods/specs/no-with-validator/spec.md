# Spec Delta

## Purpose
`no_with`, which refuses Python's `with` statements; this delta records only
the wording of its `async with` row.

## ADDED Requirements

### Requirement: async with is refused without pointing at a removed ban
The validator SHALL refuse `async with` with a sentence that does not point
at an `async def` ban.

#### Scenario: An async with block
- **WHEN** an async method contains `async with cm: pass`
- **THEN** validation fails with `async with is forbidden — POOP enters no asynchronous context manager`
