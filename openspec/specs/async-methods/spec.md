# async-methods Specification

## Purpose
An `async def` written as a direct statement of a class body: a method whose
send answers a coroutine, held to the same return and variadic rules as a
synchronous method.

## Requirements

### Requirement: An async def in a class body is a method
An `async def` that is a direct statement of a class body SHALL pass
validation and be sent like any other method. Sending it SHALL run none of
its body and SHALL answer a coroutine.

#### Scenario: Sending an async method runs nothing
- **WHEN** a program defines `class Page(Object)` with `async def fetch(self): "ran".print()` and runs `Page().fetch()` without awaiting it
- **THEN** nothing is printed

#### Scenario: Awaiting it runs the body
- **WHEN** the same program runs `Async.run(Page().fetch())`
- **THEN** it prints `ran`

### Requirement: An async def outside a class body is refused
An `async def` at module level or nested in a method SHALL be refused as a
free function.

#### Scenario: Module level
- **WHEN** a program contains `async def f(): pass` at module level
- **THEN** validation fails with `free async functions are forbidden — define methods inside a class (use a lambda for a local block)`

### Requirement: An async method answers POOP values when awaited
An awaited async method SHALL answer POOP's `none` when it falls off its end
or uses a bare `return`, and its `*args` and `**kwargs` SHALL be POOP
collections, as a synchronous method's are.

#### Scenario: Falling off the end
- **WHEN** an async method has no `return` and a program prints `Async.run(obj.m()).is_none()`
- **THEN** it prints `True`

#### Scenario: Variadic arguments
- **WHEN** a class defines `async def m(self, *args): return args.len()` and a program prints `Async.run(obj.m(1, 2))`
- **THEN** it prints `2`

#### Scenario: A docstring stays a docstring
- **WHEN** an async method's body opens with a string literal
- **THEN** that string is the method's docstring and is not evaluated on each send

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
