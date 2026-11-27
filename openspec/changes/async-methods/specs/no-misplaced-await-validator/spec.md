# Spec Delta

## Purpose
`no_misplaced_await`, which refuses every use of the `await_` selector the
rewrite to `await` cannot honour, before CPython would answer it with a raw
`SyntaxError` about code the program never wrote.

## ADDED Requirements

### Requirement: await_() is sent only directly inside an async method
The validator SHALL refuse `x.await_()` whose nearest enclosing function is
not an `async def`, keeping CPython's sentence and adding where to send it.
A block's own body SHALL count as its nearest function.

#### Scenario: Module level
- **WHEN** a program contains `obj.fetch().await_()` at module level
- **THEN** validation fails with `'await' outside async function — send await_() inside an async def method`

#### Scenario: A synchronous method
- **WHEN** a `def` method contains `self.fetch().await_()`
- **THEN** validation fails with `'await' outside async function — send await_() inside an async def method`

#### Scenario: Inside a block
- **WHEN** an async method contains `ok.if_true(lambda: self.fetch().await_())`
- **THEN** validation fails with `'await' outside async function — a block cannot await; let it answer the coroutine and send await_() to that answer`

### Requirement: await_ is sent with no arguments
The validator SHALL refuse `await_` sent with any positional or keyword
argument.

#### Scenario: An argument
- **WHEN** an async method contains `c.await_(1)`
- **THEN** validation fails with `await_() takes no arguments (1 given)`

### Requirement: await_ is sent, never read
The validator SHALL refuse `await_` read as an attribute without being
called.

#### Scenario: Passed as a block
- **WHEN** an async method contains `f = c.await_`
- **THEN** validation fails with `await_ is a message — send it: x.await_()`

### Requirement: await_ is a reserved selector
The validator SHALL refuse a method named `await_`, synchronous or async,
since every `x.await_()` is rewritten and would never reach it.

#### Scenario: Defining await_
- **WHEN** a class body contains `def await_(self): pass`
- **THEN** validation fails with `await_ is reserved — POOP sends it to await a coroutine; name the method something else`
