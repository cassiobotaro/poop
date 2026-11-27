# no-with-validator Specification

## Purpose
`no_with`, which refuses Python's `with` statements; this delta records only
the wording of its `async with` row.

## Requirements

### Requirement: async with is refused without pointing at a removed ban
The validator SHALL refuse `async with` and name `AsyncWith` as its
substitute.

#### Scenario: An async with block
- **WHEN** an async method contains `async with cm: pass`
- **THEN** validation fails with `async with is forbidden — use AsyncWith(lambda: cm).do(lambda resource: …).await_() instead`
