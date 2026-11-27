## ADDED Requirements

### Requirement: An async property answers a coroutine
An `async def` decorated with `@property` SHALL answer a coroutine when read,
the same value a sent async method answers. Reading it SHALL run none of its
body, and awaiting it SHALL answer the getter's value.

#### Scenario: Reading it runs nothing
- **WHEN** a class defines `@property` over `async def total(self): "ran".print()` and a program runs `obj.total.print()`
- **THEN** it prints `<coroutine>` and does not print `ran`

#### Scenario: The raw coroutine's attributes are unreachable
- **WHEN** a program reads `obj.total.cr_frame`
- **THEN** an `AttributeError` is raised reading `coroutine does not understand #cr_frame — try :methods to list its messages`

#### Scenario: Awaiting it answers the getter's value
- **WHEN** the getter answers `41` and an async method runs `(self.total.await_() + 1).print()`
- **THEN** it prints `42`
