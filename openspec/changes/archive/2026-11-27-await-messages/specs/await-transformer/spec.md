## ADDED Requirements

### Requirement: A receiver that cannot be awaited is refused in POOP's words
Sending `await_()` to a value that cannot be awaited SHALL raise a
`TypeError` naming the receiver's class and the remedy, wherever the failure
is read: the uncaught report and `Error.message()`.

#### Scenario: Awaiting an int
- **WHEN** an async method runs `self.sync().await_()` where `sync` is a synchronous method answering `1`
- **THEN** a `TypeError` is raised reading `int cannot be awaited — send #await_ to a coroutine, the value an async method answers`

#### Scenario: Caught and read
- **WHEN** an async method `bad` runs `self.sync().await_()`, and another prints `Try(lambda: self.bad()).except_(TypeError, lambda e: e.message()).await_()`
- **THEN** it prints `int cannot be awaited — send #await_ to a coroutine, the value an async method answers`
