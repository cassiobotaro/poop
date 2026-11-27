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
