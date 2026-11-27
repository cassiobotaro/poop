# await-transformer Specification

## Purpose
`x.await_()`, the message that awaits `x` inside an async method, written as
a message because `await` is a prefix keyword and `x.await` does not parse.

## Requirements

### Requirement: await_() awaits its receiver
Inside an async method, sending `await_()` with no arguments to an
expression SHALL suspend the method until that expression's awaitable
completes, and SHALL answer its value.

#### Scenario: Awaiting a method's answer
- **WHEN** an async method runs `self.fetch().await_().print()` and `fetch` answers `"ok"`
- **THEN** it prints `ok`

#### Scenario: Chained left to right
- **WHEN** an async method runs `self.client().await_().get("x").await_().print()` where both are async methods and `get` answers its argument
- **THEN** it prints `x`

### Requirement: A block answers the coroutine and the method awaits it
A block SHALL be able to answer a coroutine that the enclosing async method
then awaits, so a conditional await is written without awaiting inside the
block.

#### Scenario: A conditional await
- **WHEN** an async method runs `flag.if_true_if_false(lambda: self.a(), lambda: self.b()).await_().print()` with `flag` true and `a` answering `"a"`
- **THEN** it prints `a`

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
