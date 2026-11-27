# Spec Delta

## Purpose
`no_async`, which refuses the `await` keyword and names the message that
replaces it; `async def` itself is judged by where it is written.

## ADDED Requirements

### Requirement: await is refused with its substitute
The validator SHALL refuse an `await` expression wherever it is written,
module level included, and name `x.await_()` as its substitute.

#### Scenario: Inside an async method
- **WHEN** an async method contains `await self.fetch()`
- **THEN** validation fails with `await is forbidden — use x.await_() instead`

#### Scenario: At module level
- **WHEN** a program contains `await x` at module level
- **THEN** validation fails with `await is forbidden — use x.await_() instead`, not a raw CPython `SyntaxError`

### Requirement: async def is not refused by this validator
The validator SHALL report nothing for an `async def`; whether one is legal
is decided by where it is written.

#### Scenario: An async method
- **WHEN** a class body contains `async def fetch(self): pass`
- **THEN** this validator reports nothing
