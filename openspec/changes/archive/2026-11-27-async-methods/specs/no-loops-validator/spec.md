# Spec Delta

## Purpose
`no_loops`, which refuses Python's loop statements; this delta records only
the wording of its `async for` row.

## ADDED Requirements

### Requirement: async for is refused for want of an asynchronous iterator
The validator SHALL refuse `async for` with a sentence that does not point
at an `async def` ban, since `async def` is a method in a class body.

#### Scenario: An async for loop
- **WHEN** an async method contains `async for x in xs: pass`
- **THEN** validation fails with `async for loops are forbidden — no POOP value is an asynchronous iterator`
