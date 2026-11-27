# coroutine-type Specification

## Purpose
The value an async method answers before it is awaited: a POOP object that
can be awaited once, answers `Object`'s messages, and exposes none of the raw
coroutine's attributes.

## Requirements

### Requirement: A coroutine is a POOP value
The value an async method answers SHALL answer `Object`'s messages, print as
`<coroutine>`, and refuse a message it does not understand in POOP's words.

#### Scenario: Printing a coroutine
- **WHEN** a program runs `obj.fetch().print()` on an async method `fetch`
- **THEN** it prints `<coroutine>` and the body of `fetch` does not run

#### Scenario: Its class is named coroutine
- **WHEN** a program prints `obj.fetch().class_().name()`
- **THEN** it prints `coroutine`

#### Scenario: The raw coroutine's attributes are unreachable
- **WHEN** a program reads `obj.fetch().cr_frame`
- **THEN** an `AttributeError` is raised reading `coroutine does not understand #cr_frame — try :methods to list its messages`

### Requirement: A coroutine is awaited once
Awaiting a coroutine SHALL run the method's body and answer its value.
Awaiting the same coroutine a second time SHALL fail as CPython does.

#### Scenario: Awaiting answers the method's value
- **WHEN** `fetch` answers `"ok"` and an async method runs `obj.fetch().await_().print()`
- **THEN** it prints `ok`

#### Scenario: A second await
- **WHEN** an async method holds `c = obj.fetch()` and runs `c.await_()` twice
- **THEN** a `RuntimeError` is raised reading `cannot reuse already awaited coroutine`

### Requirement: A coroutine never awaited is reported as CPython reports it
A coroutine that is discarded without being awaited SHALL emit CPython's
`RuntimeWarning` and SHALL NOT fail the program.

#### Scenario: A forgotten await
- **WHEN** a program runs `obj.fetch()` and discards the answer
- **THEN** the program exits successfully and stderr carries `RuntimeWarning: coroutine 'Page.fetch' was never awaited`
